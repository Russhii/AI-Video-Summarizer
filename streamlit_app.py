import os

import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("API_BASE_URL", "http://localhost:8000").rstrip("/")
API_KEY = os.getenv("APP_API_KEY", "")

st.set_page_config(
    page_title="VideoBrief | AI Video Assistant",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500;12..96,600;12..96,700&family=Figtree:wght@400;500;600;700&display=swap');

    :root {
        --paper: #fbf5ea;
        --surface: #fffdf8;
        --sand: #f3e8d6;
        --ink: #2e1f1a;
        --muted: #806f64;
        --line: #eadcc6;
        --marigold: #f4a83a;
        --marigold-deep: #e39418;
        --mulberry: #3d1f2b;
        --rose: #f6d5c4;
    }

    html, body, .stApp, .stMarkdown, p, label, input, textarea, button, [data-baseweb="tab"] {
        font-family: 'Figtree', sans-serif;
    }
    /* keep Streamlit's icon font intact */
    [data-testid="stIconMaterial"], .material-icons, .material-symbols-rounded {
        font-family: 'Material Symbols Rounded' !important;
    }

    .stApp { background: var(--paper); color: var(--ink); }
    .stApp h1, .stApp h2, .stApp h3, .stApp h4 {
        font-family: 'Bricolage Grotesque', sans-serif;
        letter-spacing: -0.03em;
        color: var(--ink);
        padding: 0;
    }
    .stApp h2, .stApp h3 { font-weight: 600; }
    .stApp label, .stApp [data-testid="stWidgetLabel"] p { color: var(--ink); font-weight: 500; }
    .block-container { max-width: 1120px; padding-top: 2rem; padding-bottom: 4rem; }

    /* header + footer chrome */
    [data-testid="stHeader"] { background: transparent; }
    footer, [data-testid="stFooter"] { visibility: hidden; }

    /* sidebar */
    [data-testid="stSidebar"] { background: var(--sand); border-right: 1px solid var(--line); }
    .brand {
        font: 700 1.45rem 'Bricolage Grotesque', sans-serif;
        letter-spacing: -.04em;
        margin: .6rem 0 1.5rem;
        display: flex; align-items: center; gap: .55rem;
    }
    .brand .dot {
        width: 1.9rem; height: 1.9rem; border-radius: 50%;
        background: var(--marigold);
        display: inline-flex; align-items: center; justify-content: center;
        font-size: .95rem;
    }

    .small-label { font-size: .9rem; color: var(--muted); font-weight: 600; }

    /* hero */
    .stApp .hero {
        background: var(--mulberry);
        border-radius: 28px;
        padding: 2.6rem 2.8rem;
        margin: .4rem 0 2rem;
        display: flex; flex-wrap: wrap; gap: 2rem; justify-content: space-between; align-items: flex-end;
    }
    .stApp .hero .copy { flex: 1 1 340px; }
    .stApp .hero .small-label { color: var(--marigold); }
    .stApp .hero h1 {
        color: #fff6e8;
        font-size: clamp(2.3rem, 5vw, 3.6rem);
        line-height: 1.04;
        margin: .6rem 0 .9rem;
        font-weight: 700;
    }
    .stApp .hero p { color: #e6cfc4; max-width: 520px; margin: 0; line-height: 1.6; }
    .stApp .hero ul { list-style: none; margin: 0; padding: 0; display: flex; flex-wrap: wrap; gap: .5rem; max-width: 300px; }
    .stApp .hero li {
        background: rgba(255, 246, 232, .1);
        border: 1px solid rgba(255, 246, 232, .18);
        color: #fff6e8;
        border-radius: 999px;
        padding: .4rem .9rem;
        font-size: .88rem;
        font-weight: 500;
    }

    /* cards */
    [data-testid="stMetric"] {
        background: var(--surface);
        border: 1px solid var(--line);
        border-radius: 18px;
        padding: 1.1rem 1.2rem;
    }
    [data-testid="stMetricLabel"] p { color: var(--muted); }
    [data-testid="stMetricValue"] { font-family: 'Bricolage Grotesque', sans-serif; letter-spacing: -.02em; }
    [data-testid="stForm"] {
        background: var(--surface);
        border: 1px solid var(--line);
        border-radius: 22px;
        padding: 1.6rem;
        box-shadow: 0 10px 30px -18px rgba(61, 31, 43, .35);
    }

    /* inputs */
    .stTextInput input, .stTextArea textarea, [data-baseweb="select"] > div {
        border-radius: 12px;
        background: #fff;
        border-color: var(--line);
        color: var(--ink);
    }
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: var(--marigold-deep);
        box-shadow: 0 0 0 3px rgba(244, 168, 58, .3);
    }
    .stTextInput [data-baseweb="input"], .stTextArea [data-baseweb="textarea"] { border-radius: 12px; }

    /* buttons */
    div.stButton > button[kind="primary"],
    div.stFormSubmitButton > button[kind="primary"],
    [data-testid="stBaseButton-primary"],
    [data-testid="stBaseButton-primaryFormSubmit"] {
        background: var(--marigold);
        color: var(--ink);
        border: 0;
        font-weight: 700;
        border-radius: 999px;
        padding: .6rem 1.5rem;
        transition: background .15s ease, transform .15s ease;
    }
    div.stButton > button[kind="primary"]:hover,
    div.stFormSubmitButton > button[kind="primary"]:hover,
    [data-testid="stBaseButton-primary"]:hover,
    [data-testid="stBaseButton-primaryFormSubmit"]:hover {
        background: var(--marigold-deep);
        color: var(--ink);
    }
    div.stButton > button[kind="primary"]:focus-visible,
    div.stFormSubmitButton > button[kind="primary"]:focus-visible {
        outline: 3px solid var(--mulberry); outline-offset: 2px;
    }
    [data-testid="stBaseButton-secondary"] {
        border-radius: 999px;
        border: 1px solid var(--line);
        background: var(--surface);
        color: var(--ink);
        font-weight: 600;
    }
    [data-testid="stBaseButton-secondary"]:hover { border-color: var(--marigold-deep); color: var(--ink); }

    /* tabs */
    .stTabs [data-baseweb="tab-list"] { gap: 1.4rem; border-bottom: 1px solid var(--line); }
    .stTabs [data-baseweb="tab"] { height: 3rem; }
    .stTabs [data-baseweb="tab-highlight"] { background: var(--marigold-deep); height: 3px; border-radius: 3px; }
    .stTabs [aria-selected="true"] p { font-weight: 700; }

    /* chat */
    [data-testid="stChatMessage"] {
        background: var(--surface);
        border: 1px solid var(--line);
        border-radius: 18px;
        padding: 1rem 1.2rem;
    }

    /* alerts */
    [data-testid="stAlert"] { border-radius: 14px; }
    hr { border-color: var(--line); }

    /* force readable sidebar text in any theme */
    [data-testid="stSidebar"],
    [data-testid="stSidebar"] * {
        color: var(--ink) !important;
    }
    [data-testid="stSidebar"] [data-testid="stCaptionContainer"],
    [data-testid="stSidebar"] [data-testid="stCaptionContainer"] * {
        color: var(--muted) !important;
    }

    /* force readable text in the main area (hero keeps its own colors) */
    .stApp [data-testid="stMarkdownContainer"] p,
    .stApp [data-testid="stMarkdownContainer"] li,
    .stApp [data-testid="stWidgetLabel"] *,
    .stApp [data-baseweb="tab"] p {
        color: var(--ink);
    }
    .stApp .hero p { color: #e6cfc4; }
    .stApp .hero h1 { color: #fff6e8; }
    .stApp .hero .small-label { color: var(--marigold); }
    .stApp .hero li { color: #fff6e8; }

    @media (max-width: 640px) {
        .stApp .hero { padding: 1.8rem 1.4rem; border-radius: 22px; }
    }
    @media (prefers-reduced-motion: reduce) {
        * { transition: none !important; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def api_headers(api_key: str) -> dict[str, str]:
    return {"X-API-Key": api_key} if api_key else {}


def show_api_error(error: requests.RequestException) -> None:
    response = getattr(error, "response", None)
    if response is not None:
        try:
            detail = response.json().get("detail", response.text)
        except ValueError:
            detail = response.text
        st.error(f"Backend request failed ({response.status_code}): {detail}")
    else:
        st.error(f"Could not reach the backend: {error}")


def mindmap_lines(node: dict, depth: int = 0) -> list[str]:
    topic = node.get("topic")
    if not isinstance(topic, str) or not topic.strip():
        return []

    lines = [f"{'  ' * depth}- {topic.strip()}"]
    children = node.get("children", [])
    if isinstance(children, list):
        for child in children:
            if isinstance(child, dict):
                lines.extend(mindmap_lines(child, depth + 1))
    return lines


api_url = API_URL
api_key = API_KEY

with st.sidebar:
    st.markdown('<div class="brand"><span class="dot">🎬</span>videobrief</div>', unsafe_allow_html=True)

    try:
        health_response = requests.get(f"{api_url}/health", timeout=3)
        health_response.raise_for_status()
        st.success("Backend connected", icon="🟢")
    except requests.RequestException:
        st.warning("Backend offline. Please try again shortly.", icon="⚠️")

    st.divider()
    st.caption("Paste a YouTube link to create a video brief.")


st.markdown(
    """
    <div class="hero">
      <div class="copy">
        <div class="small-label">Your meetings, made useful</div>
        <h1>Watch less.<br>Understand more.</h1>
        <p>Turn long videos into clear summaries, decisions, action items, and a transcript you can ask questions about.</p>
      </div>
      <ul>
        <li>Summary</li><li>Action items</li><li>Decisions</li><li>Transcript</li><li>Ask the video</li>
      </ul>
    </div>
    """,
    unsafe_allow_html=True,
)

input_tab = st.container()
result_tab = st.container()

with input_tab:
    st.subheader("Start with a video")
    st.write("Paste a YouTube link, then select the language spoken in the video.")
    with st.form("analysis_form"):
        video_url = st.text_input(
            "YouTube URL",
            placeholder="https://www.youtube.com/watch?v=...",
        )

        language = st.selectbox(
            "Audio language",
            ["english", "hinglish"],
            format_func=lambda value: "English" if value == "english" else "Hinglish",
        )
        submitted = st.form_submit_button("Generate my video brief", type="primary")

    if submitted:
        if not video_url.strip():
            st.error("Paste a YouTube URL to continue.")
        else:
            try:
                with st.spinner("Sending your video to the backend..."):
                    response = requests.post(
                        f"{api_url}/jobs/url",
                        headers=api_headers(api_key),
                        json={"url": video_url.strip(), "language": language},
                        timeout=30,
                    )
                    response.raise_for_status()
                st.session_state.job_id = response.json()["job_id"]
                st.session_state.result = None
                st.session_state.chat_history = []
                st.session_state.mindmap = None
                st.session_state.quiz = None
                st.session_state.quiz_submitted = False
                st.session_state.quiz_version = 0
                st.success("Analysis started. You can follow its progress below.")
            except requests.RequestException as error:
                show_api_error(error)

    if st.session_state.get("job_id") and not st.session_state.get("result"):
        st.markdown("#### Analysis progress")

        @st.fragment(run_every=3)
        def render_job_status() -> None:
            try:
                response = requests.get(
                    f"{api_url}/jobs/{st.session_state.job_id}",
                    headers=api_headers(api_key),
                    timeout=10,
                )
                response.raise_for_status()
                job = response.json()
            except requests.RequestException as error:
                show_api_error(error)
                return

            status = job.get("status", "unknown")
            if status == "done":
                result = job.get("result")
                if not isinstance(result, dict):
                    st.error("The backend marked this job complete but returned no analysis result.")
                    return
                st.session_state.result = result
                st.success("Your video brief is ready.")
                st.rerun()
            elif status == "failed":
                st.error(f"Analysis failed: {job.get('error') or 'The backend did not provide an error message.'}")
            else:
                st.info(f"Status: **{status.capitalize()}** — this can take a few minutes for longer videos.")
                st.caption("This panel refreshes automatically.")

        render_job_status()

with result_tab:
    result = st.session_state.get("result")
    if not result:
        st.info("Your summary, transcript, and Q&A will appear here after an analysis finishes.")
    else:
        st.divider()
        st.markdown('<div class="small-label">Your video brief</div>', unsafe_allow_html=True)
        st.title(result.get("title") or "Untitled video")
        transcript = result.get("transcript", "")
        word_count = len(transcript.split())
        metrics = st.columns(3)
        metrics[0].metric("Transcript words", f"{word_count:,}")
        metrics[1].metric("Summary", "Ready")
        metrics[2].metric("Transcript Q&A", "Ready")

        (
            summary_tab,
            actions_tab,
            decisions_tab,
            questions_tab,
            transcript_tab,
            chat_tab,
            mindmap_tab,
            quiz_tab,
        ) = st.tabs(
            [
                "Summary",
                "Action items",
                "Decisions",
                "Open questions",
                "Transcript",
                "Ask the video",
                "Mind map",
                "Quiz",
            ]
        )
        with summary_tab:
            st.markdown(result.get("summary") or "No summary was returned.")
        with actions_tab:
            st.markdown(result.get("action_items") or "No action items were returned.")
        with decisions_tab:
            st.markdown(result.get("key_decisions") or "No decisions were returned.")
        with questions_tab:
            st.markdown(result.get("open_questions") or "No open questions were returned.")
        with transcript_tab:
            st.text_area("Full transcript", transcript, height=420, label_visibility="collapsed")
            st.download_button(
                "Download transcript",
                data=transcript,
                file_name="video-transcript.txt",
                mime="text/plain",
            )
        with chat_tab:
            for message in st.session_state.get("chat_history", []):
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

            with st.form("chat_form", clear_on_submit=True):
                question = st.text_input(
                    "Ask a question",
                    placeholder="What were the main takeaways?",
                    label_visibility="collapsed",
                )
                ask = st.form_submit_button("Ask", type="primary")
            if ask and question.strip():
                st.session_state.chat_history.append({"role": "user", "content": question.strip()})
                try:
                    response = requests.post(
                        f"{api_url}/jobs/{st.session_state.job_id}/chat",
                        headers=api_headers(api_key),
                        json={"question": question.strip()},
                        timeout=120,
                    )
                    response.raise_for_status()
                    answer = response.json()["answer"]
                    st.session_state.chat_history.append({"role": "assistant", "content": answer})
                    st.rerun()
                except requests.RequestException as error:
                    st.session_state.chat_history.pop()
                    show_api_error(error)

        with mindmap_tab:
            mindmap = st.session_state.get("mindmap")
            if not mindmap and st.button("Generate mind map", key="generate_mindmap"):
                try:
                    with st.spinner("Creating the mind map..."):
                        response = requests.post(
                            f"{api_url}/jobs/{st.session_state.job_id}/mindmap",
                            headers=api_headers(api_key),
                            timeout=180,
                        )
                        response.raise_for_status()
                        payload = response.json()
                    generated_mindmap = payload.get("mindmap")
                    if (
                        not isinstance(generated_mindmap, dict)
                        or not isinstance(generated_mindmap.get("title"), str)
                        or not isinstance(generated_mindmap.get("branches"), list)
                    ):
                        st.error("The backend returned an invalid mind map.")
                    else:
                        st.session_state.mindmap = generated_mindmap
                        mindmap = generated_mindmap
                except requests.RequestException as error:
                    show_api_error(error)

            if mindmap:
                st.subheader(mindmap["title"])
                lines = []
                for branch in mindmap["branches"]:
                    if isinstance(branch, dict):
                        lines.extend(mindmap_lines(branch))
                if lines:
                    st.markdown("\n".join(lines))
                else:
                    st.info("No mind-map branches were returned.")

        with quiz_tab:
            quiz = st.session_state.get("quiz")
            if not quiz and st.button("Create quiz", key="generate_quiz"):
                try:
                    with st.spinner("Creating your quiz..."):
                        response = requests.post(
                            f"{api_url}/jobs/{st.session_state.job_id}/quiz",
                            headers=api_headers(api_key),
                            timeout=180,
                        )
                        response.raise_for_status()
                        payload = response.json()
                    generated_quiz = payload.get("quiz")
                    if (
                        not isinstance(generated_quiz, dict)
                        or not isinstance(generated_quiz.get("questions"), list)
                        or not generated_quiz["questions"]
                    ):
                        st.error("The backend returned an invalid quiz.")
                    else:
                        st.session_state.quiz = generated_quiz
                        st.session_state.quiz_submitted = False
                        st.session_state.quiz_version = (
                            st.session_state.get("quiz_version", 0) + 1
                        )
                        quiz = generated_quiz
                except requests.RequestException as error:
                    show_api_error(error)

            if quiz:
                quiz_version = st.session_state.get("quiz_version", 0)
                quiz_submitted = st.session_state.get("quiz_submitted", False)

                with st.form("video_quiz_form"):
                    for index, question in enumerate(quiz["questions"]):
                        if (
                            not isinstance(question, dict)
                            or not isinstance(question.get("question"), str)
                            or not isinstance(question.get("options"), list)
                            or not question["options"]
                        ):
                            st.error(f"Quiz question {index + 1} is invalid.")
                            continue

                        st.markdown(f"**{index + 1}. {question['question']}**")
                        st.radio(
                            "Choose an answer",
                            question["options"],
                            index=None,
                            key=(
                                f"quiz_answer_{st.session_state.job_id}_"
                                f"{quiz_version}_{index}"
                            ),
                            disabled=quiz_submitted,
                            label_visibility="collapsed",
                        )

                    submitted = st.form_submit_button(
                        "Check my answers",
                        disabled=quiz_submitted,
                    )

                if submitted:
                    score = 0
                    for index, question in enumerate(quiz["questions"]):
                        answer_key = (
                            f"quiz_answer_{st.session_state.job_id}_"
                            f"{quiz_version}_{index}"
                        )
                        if st.session_state.get(answer_key) == question.get("correct_answer"):
                            score += 1

                    st.session_state.quiz_score = score
                    st.session_state.quiz_submitted = True
                    st.rerun()

                if quiz_submitted:
                    st.success(
                        f"Your score: {st.session_state.quiz_score} "
                        f"out of {len(quiz['questions'])}"
                    )
                    for index, question in enumerate(quiz["questions"]):
                        st.markdown(f"**{index + 1}. {question['question']}**")
                        st.write(f"Correct answer: {question['correct_answer']}")
                        st.caption(question.get("explanation", ""))

                    if st.button("Try quiz again", key="retry_quiz"):
                        st.session_state.quiz_submitted = False
                        st.session_state.quiz_version = quiz_version + 1
                        st.rerun()