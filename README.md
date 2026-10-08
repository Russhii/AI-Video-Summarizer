# VideoBrief — AI Video Assistant

VideoBrief turns a YouTube video or local audio/video file into a concise, useful brief. It transcribes the audio, creates a summary, extracts action items, decisions, and open questions, and lets you ask questions about the transcript.

The project includes a Streamlit web interface, a FastAPI backend, and a command-line entry point.

## Demo video

<video controls width="100%">
  <source src="./video.mp4" type="video/mp4">
  Your browser does not support the video tag.
</video>

[Open the demo video](./video.mp4)

## Overview

VideoBrief is designed to help users quickly understand long-form video content without watching the entire recording. It supports both YouTube links and local media files, making it useful for meetings, lectures, tutorials, product demos, and interviews.

## Features

- Process YouTube videos or local audio/video files.
- Transcribe English audio locally with Whisper.
- Transcribe Hinglish audio with Sarvam AI and translate it to English.
- Generate a clear title, executive summary, action items, key decisions, open questions, a content mind map, and a quiz with Groq.
- Enable transcript-grounded chat using retrieval-augmented generation (RAG).
- Store transcript embeddings in a local Chroma vector database for semantic Q&A.
- Download the full transcript from the Streamlit app UI.
- Explore key ideas visually with an AI-generated mind map and reinforce learning with quiz questions.
- Work through a simple three-part workflow: upload or paste a source, analyze, and ask questions.
- Support both web and terminal workflows through Streamlit, FastAPI, and CLI entry points.

## How it works

1. The audio processor downloads audio from a YouTube URL or converts a local media file to WAV, then splits it into chunks.
2. Whisper or Sarvam transcribes the audio, depending on the selected language.
3. Groq generates the title, summary, action items, decisions, open questions, a mind map, and a quiz.
4. The transcript is embedded and stored in Chroma. When you ask a question, the app retrieves relevant transcript chunks and sends them to the language model to produce an answer.

## Project structure

```text
.
├── api/
│   └── app.py                 # FastAPI endpoints and background video-analysis jobs
├── core/
│   ├── extractor.py           # Action items, decisions, and open-question extraction
│   ├── rag_engine.py          # Transcript question answering
│   ├── summarizer.py          # Title and summary generation
│   ├── transcriber.py         # Whisper and Sarvam transcription
│   └── vector_store.py        # Chroma storage and Hugging Face embeddings
├── services/
│   └── pipeline.py            # End-to-end analysis pipeline
├── utils/
│   └── audio_processor.py     # Audio download, conversion, and chunking
├── downloades/                # Generated/downloaded audio (created at runtime)
├── vector_db/                 # Persistent Chroma database (created at runtime)
├── main.py                    # Command-line entry point
├── streamlit_app.py           # Streamlit web application
├── Requirements.txt           # Python dependencies
├── .env                       # Local secrets and configuration (create locally)
└── .gitignore
```

`downloades/` is the directory name used by the current audio-processing code.
Both it and `vector_db/` contain generated or local data and are excluded from Git.

## Requirements

- Python 3.11 (the version noted in `Requirements.txt`)
- FFmpeg installed and available on `PATH` (used by yt-dlp and pydub to process media)
- A Groq API key for analysis and question answering
- A Sarvam API key if you want to process Hinglish audio
- Internet access to download YouTube audio, call the hosted APIs, and download the embedding model on first use

## Setup

### Windows PowerShell

From the project root:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r Requirements.txt
```

If PowerShell prevents activation, you can run the virtual environment's executables directly instead of changing the execution policy:

```powershell
.\.venv\Scripts\python.exe -m pip install -r Requirements.txt
```

Install FFmpeg separately and confirm that `ffmpeg -version` works in a new terminal.

### macOS / Linux

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r Requirements.txt
```

Install FFmpeg with your operating system's package manager and make sure `ffmpeg` is available on `PATH`.

## Configuration

Create a `.env` file in the project root. Do not commit API keys:

```dotenv
GROQ_API_KEY=your_groq_api_key

# Required only for Hinglish transcription
SARVAM_API_KEY=your_sarvam_api_key

# Optional: configure the local app API key on both the backend and frontend
APP_API_KEY=

# Optional: Streamlit uses this backend URL by default
API_BASE_URL=http://localhost:8000

# Optional: comma-separated browser origins allowed by the API; defaults to *
ALLOWED_ORIGINS=*

# Optional: Whisper model name; defaults to small
WHISPER_MODEL=small

# Optional: Sarvam model; defaults to saaras:v2.5
SARVAM_STT_MODEL=saaras:v2.5
```

`APP_API_KEY` is optional for local development. If set, the same value must be available to the FastAPI backend and Streamlit frontend. The API expects it in the `X-API-Key` request header.

## Run the application

Start the API and web interface in separate terminals from the project root.

### 1. Start the FastAPI backend

```powershell
# Windows
.\.venv\Scripts\python.exe -m uvicorn api.app:app --host 127.0.0.1 --port 8000
```

```bash
# macOS / Linux, with the virtual environment activated
python -m uvicorn api.app:app --host 127.0.0.1 --port 8000
```

The health check is available at <http://localhost:8000/health>, and the interactive API docs are at <http://localhost:8000/docs>.

### 2. Start the Streamlit frontend

```powershell
# Windows
.\.venv\Scripts\python.exe -m streamlit run streamlit_app.py
```

```bash
# macOS / Linux, with the virtual environment activated
python -m streamlit run streamlit_app.py
```

Open the local URL printed by Streamlit (usually <http://localhost:8501>). Paste a YouTube URL, choose English or Hinglish, and submit. The page displays job progress and then the results and transcript Q&A.

## Command-line usage

The CLI accepts a YouTube URL or a local media-file path:

```powershell
.\.venv\Scripts\python.exe main.py
```

Follow the prompts to enter the source and language (`english` or `hinglish`). After processing, you can ask questions in the terminal; enter `exit`, `quit`, or `q` to stop.

## API overview

The backend exposes these endpoints:

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/health` | Check whether the API is running |
| `POST` | `/jobs/url` | Start analysis of a YouTube URL |
| `GET` | `/jobs/{job_id}` | Read analysis status or completed results |
| `POST` | `/jobs/{job_id}/chat` | Ask a question about a completed analysis |

The API accepts YouTube URLs for analysis. Local file paths are supported by the command-line pipeline, not by the web API.

## Generated data and troubleshooting

- The first Whisper run downloads the configured Whisper model. The embedding model is also downloaded on first use.
- Downloaded audio and audio chunks are written to `downloades/`; Chroma data is stored in `vector_db/`.
- If the frontend reports that the backend is offline, start the FastAPI server and check `API_BASE_URL`.
- If analysis fails due to a missing Groq key, set `GROQ_API_KEY` in the project-root `.env`.
- Hinglish transcription requires `SARVAM_API_KEY`; English transcription uses the local Whisper model.
- If audio conversion or YouTube audio extraction fails, verify that FFmpeg is installed and available on `PATH`.
