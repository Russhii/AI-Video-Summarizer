from dotenv import load_dotenv
load_dotenv()  
import os
import uuid
import threading
import traceback
from typing import Dict, Literal

from fastapi import (
    FastAPI, BackgroundTasks,
    HTTPException, Depends, Header,
)
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from services.pipeline import run_pipeline
from core.rag_engine import load_rag_chain, ask_question
from core.video_learning import generate_mindmap, generate_quiz

APP_API_KEY = os.getenv("APP_API_KEY")  # optional but set it in production
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")

app = FastAPI(title="AI Video Assistant API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

JOBS: Dict[str, dict] = {}
CHAINS: Dict[str, object] = {}
PIPELINE_LOCK = threading.Semaphore(1)  # one heavy job at a time (avoids OOM)


def require_key(x_api_key: str = Header(default=None)):
    if APP_API_KEY and x_api_key != APP_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing X-API-Key")


class UrlJob(BaseModel):
    url: str
    language: Literal["english", "hinglish"] = "english"


class ChatRequest(BaseModel):
    question: str


def _collection(job_id: str) -> str:
    return f"m_{job_id[:12]}"


def _run_job(job_id: str, source: str, language: str):
    JOBS[job_id]["status"] = "queued"
    try:
        with PIPELINE_LOCK:
            JOBS[job_id]["status"] = "processing"
            result = run_pipeline(source, language, collection_name=_collection(job_id))
        result.pop("rag_chain", None)  # not serializable; reloaded on demand
        JOBS[job_id].update(status="done", result=result)
    except Exception as e:
        traceback.print_exc()
        JOBS[job_id].update(status="failed", error=str(e))


def _new_job(kind: str, language: str) -> str:
    job_id = uuid.uuid4().hex
    JOBS[job_id] = {"id": job_id, "kind": kind, "language": language,
                    "status": "queued", "result": None, "error": None, "features": {},}
    return job_id


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/jobs/url", dependencies=[Depends(require_key)])
def create_job_from_url(body: UrlJob, background: BackgroundTasks):
    if not body.url.startswith(("http://", "https://")):
        raise HTTPException(400, "url must start with http:// or https://")
    job_id = _new_job("url", body.language)
    background.add_task(_run_job, job_id, body.url, body.language)
    return {"job_id": job_id, "status": "queued"}


@app.get("/jobs/{job_id}", dependencies=[Depends(require_key)])
def get_job(job_id: str):
    job = JOBS.get(job_id)
    if not job:
        raise HTTPException(404, "Job not found")
    return job


@app.post("/jobs/{job_id}/chat", dependencies=[Depends(require_key)])
def chat(job_id: str, body: ChatRequest):
    job = JOBS.get(job_id)
    if not job:
        raise HTTPException(404, "Job not found")
    if job["status"] != "done":
        raise HTTPException(409, f"Job is {job['status']}, not done yet")
    if not body.question.strip():
        raise HTTPException(400, "Question is empty")

    if job_id not in CHAINS:
        CHAINS[job_id] = load_rag_chain(_collection(job_id))
    answer = ask_question(CHAINS[job_id], body.question)
    return {"answer": answer}


def _get_completed_transcript(job_id: str) -> tuple[dict, str]:
    job = JOBS.get(job_id)

    if not job:
        raise HTTPException(404, "Job not found")

    if job["status"] != "done":
        raise HTTPException(409, f"Job is {job['status']}, not done yet")

    result = job.get("result")
    transcript = result.get("transcript") if isinstance(result, dict) else None

    if not transcript:
        raise HTTPException(500, "Completed job has no transcript")

    return job, transcript


@app.post("/jobs/{job_id}/mindmap", dependencies=[Depends(require_key)])
def create_mindmap(job_id: str):
    job, transcript = _get_completed_transcript(job_id)

    if "mindmap" not in job["features"]:
        job["features"]["mindmap"] = generate_mindmap(transcript)

    return {"mindmap": job["features"]["mindmap"]}


@app.post("/jobs/{job_id}/quiz", dependencies=[Depends(require_key)])
def create_quiz(job_id: str):
    job, transcript = _get_completed_transcript(job_id)

    if "quiz" not in job["features"]:
        job["features"]["quiz"] = generate_quiz(transcript)

    return {"quiz": job["features"]["quiz"]}