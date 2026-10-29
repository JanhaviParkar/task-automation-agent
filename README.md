---
title: Task Automation Agent Gemini
emoji: 🔎
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
---

# Task-Automation Agent (Gemini + DuckDuckGo)

A Streamlit application for Experiment 9 and Experiment 10. It searches the web with DuckDuckGo and asks Gemini to synthesize the results into exactly three concise bullet points.

## Run locally

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
$env:GEMINI_API_KEY="YOUR_REAL_KEY"
streamlit run app.py
```

Open the local URL shown in the terminal, normally http://localhost:8501.

## Run tests

```powershell
python -m unittest discover -s tests -v
```

## Run with Docker (PowerShell)

```powershell
docker build -t task-automation-agent .
docker run --rm -p 7860:7860 -e GEMINI_API_KEY="YOUR_REAL_KEY" task-automation-agent
```

Open http://localhost:7860.

Do not commit your real key, `.env`, or `.streamlit/secrets.toml`.

## Pipeline

Developer → Git push → GitHub Actions (install dependencies, run tests, build Docker image) → deployment platform builds/runs the container → user submits topic → DuckDuckGo search → Gemini summary → logs.

## Hosting

This container listens on port 7860, suitable for a Hugging Face Docker Space. In the Space settings, create a runtime secret named `GEMINI_API_KEY` with the real key. Do not add the key to this README, Dockerfile, or repository.
