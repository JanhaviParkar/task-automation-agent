import logging
import os
import time
from datetime import datetime, timezone

import streamlit as st
from ddgs import DDGS
from google import genai

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger("task_agent")

MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")


def search_web(topic: str, max_results: int = 5) -> str:
    """Search the web and return a compact text block of titles, snippets, and URLs."""
    if not topic or not topic.strip():
        raise ValueError("Please enter a topic.")
    logger.info("Search started for topic=%r", topic[:120])
    rows = []
    with DDGS() as ddgs:
        results = ddgs.text(topic.strip(), max_results=max_results)
        for item in results:
            title = item.get("title", "Untitled")
            body = item.get("body", "")
            url = item.get("href", "")
            rows.append(f"Title: {title}\nSnippet: {body}\nURL: {url}")
    if not rows:
        raise RuntimeError("The web search returned no results. Try a more specific topic.")
    return "\n\n".join(rows)


def summarize_results(topic: str, search_results: str, temperature: float = 0.2) -> str:
    """Use Gemini to summarize search results into exactly three bullet points."""
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError(
            "Gemini API key is missing. Set GEMINI_API_KEY in your environment or hosting secrets."
        )

    client = genai.Client(api_key=api_key)
    prompt = f"""
You are a careful research assistant. Summarize the supplied web search results about:
{topic}

Use only information supported by the supplied results. Do not invent facts. If evidence is
unclear or conflicting, say so. Return exactly three concise bullet points. Each bullet should
communicate one useful finding. Do not add an introduction, conclusion, or extra bullets.
Include a source URL in a bullet when a relevant URL is available.

Search results:
{search_results}
"""
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config={"temperature": temperature},
    )
    text = (response.text or "").strip()
    if not text:
        raise RuntimeError("Gemini returned an empty response. Please try again.")
    return text


def run_agent(topic: str, temperature: float = 0.2) -> str:
    """One-call workflow: search first, then summarize."""
    start = time.perf_counter()
    try:
        results = search_web(topic)
        brief = summarize_results(topic, results, temperature)
        elapsed = time.perf_counter() - start
        logger.info("Request succeeded topic=%r duration_seconds=%.2f", topic[:120], elapsed)
        return brief
    except Exception:
        elapsed = time.perf_counter() - start
        logger.exception("Request failed topic=%r duration_seconds=%.2f", topic[:120], elapsed)
        raise


st.set_page_config(page_title="Task Automation Agent", page_icon="🔎", layout="centered")
st.title("🔎 Gemini Research Assistant")
st.write("Enter a topic. The agent searches the web and uses Gemini to create a three-point research brief.")

with st.sidebar:
    st.subheader("Settings")
    temperature = st.slider("Gemini temperature", min_value=0.0, max_value=1.0, value=0.2, step=0.1)
    st.caption(f"Model: {MODEL_NAME}")
    st.caption("Keep your API key in an environment variable or hosting secret. Never paste it into this app.")

topic = st.text_input("Research topic", placeholder="e.g., recent advances in renewable energy")
if st.button("Search and summarize", type="primary"):
    if not topic.strip():
        st.warning("Please enter a topic first.")
    else:
        try:
            with st.status("Running the agent...", expanded=True) as status:
                st.write("Stage 1/2: Searching the web with DuckDuckGo...")
                results = search_web(topic)
                st.write("Stage 2/2: Summarizing the search results with Gemini...")
                brief = summarize_results(topic, results, temperature)
                status.update(label="Research brief ready", state="complete", expanded=False)
            st.subheader("Three-point research brief")
            st.markdown(brief)
        except Exception as exc:
            st.error(f"Could not complete the request: {exc}")
            st.info("Check your internet connection, Gemini API key, API quota, and terminal/hosting logs.")
