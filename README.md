# TingeStudies

A lecture study assistant app that lets students upload course materials and ask questions based only on the uploaded files.

## Features

- Accepts PDF, DOCX, and PPTX uploads only
- Restricts Q&A to the uploaded file contents only
- Keeps chat history in SQLite and only sends the last 5 relevant messages to the model
- Enables chat with an OpenAI-backed assistant
- Generates study questions from the uploaded materials on a chosen topic
- Designed to be easy to push to GitHub and continue building

## Model configuration

This app pulls its OpenAI settings from your local environment and matches the model family already used in your CrewAI project:

- `OPENAI_API_KEY`
- `OPENAI_MODEL=openai/gpt-5.4-mini`

The `.env` file is intentionally ignored by Git so it stays local to your machine.

## Local setup

### 1) Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2) Frontend

```bash
cd frontend
npm install
npm run dev
```

Then open the frontend locally (usually `http://localhost:5173`) and upload lecture files.

## How to test the app

1. Start the backend in one terminal.
2. Start the frontend in another terminal.
3. Upload at least one PDF, DOCX, or PPTX file.
4. Ask a question about the uploaded content.
5. Confirm that the app blocks unsupported file types and blocks chat before upload.
6. Try the study question generator with a topic like "cell respiration" or "regression analysis".

## Render deployment

This repo includes a Docker + Render setup for deployment.

### Files included

- `Dockerfile`
- `render.yaml`
- `.dockerignore`

### Render steps

1. Push this repo to GitHub.
2. In Render, click New + Web Service.
3. Connect the GitHub repo.
4. Render will read `render.yaml` automatically.
5. Add the environment variables in Render:
   - `OPENAI_API_KEY`
   - `OPENAI_MODEL=openai/gpt-5.4-mini`
6. Deploy.

The backend serves the built frontend automatically when the Vite build is available.

## Notes

- Users cannot ask questions until files have been uploaded.
- Unsupported file types are rejected before processing.
- The app is intentionally scoped to uploaded materials only and never calls external sources.
- The AI sees only the latest relevant exchanges, which keeps costs lower and prevents the chat from ballooning in tokens.
