from pathlib import Path
from typing import List

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.config import ALLOWED_EXTENSIONS
from app.db import get_recent_messages, initialize_db, save_message
from app.rag import APP_STORAGE_DIR, StudyRAG

app = FastAPI(title="TingeStudies", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1|0\.0\.0\.0|.*\.onrender\.com|.*\.render\.com)(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

rag = StudyRAG()
initialize_db()

frontend_dist = Path(__file__).resolve().parents[2] / "frontend" / "dist"
if frontend_dist.exists():
    app.mount("/assets", StaticFiles(directory=str(frontend_dist / "assets")), name="assets")


class ChatRequest(BaseModel):
    sessionId: str
    question: str


class StudyTopicRequest(BaseModel):
    sessionId: str
    topic: str


@app.get("/api/health")
def health_check():
    return {"status": "ok"}


@app.post("/api/upload")
async def upload_files(
    session_id: str = Form(...),
    files: List[UploadFile] = File(...),
):
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded.")

    if not session_id.strip():
        raise HTTPException(status_code=400, detail="Session ID is required.")

    user_upload_dir = APP_STORAGE_DIR / session_id
    user_upload_dir.mkdir(parents=True, exist_ok=True)
    processed_files: List[str] = []

    for upload in files:
        filename = upload.filename or "uploaded_file"
        suffix = Path(filename).suffix.lower()
        if suffix not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {filename}. Only PDF, DOCX, and PPTX files are allowed.",
            )

        target_path = user_upload_dir / filename
        file_bytes = await upload.read()
        target_path.write_bytes(file_bytes)
        rag.process_upload(session_id, target_path, filename)
        processed_files.append(filename)

    return {"message": "Files uploaded successfully", "files": processed_files}


@app.post("/api/chat")
def chat_with_agent(payload: ChatRequest):
    if not payload.question.strip():
        raise HTTPException(status_code=400, detail="Please enter a question.")

    if not rag.get_session_documents(payload.sessionId):
        raise HTTPException(status_code=400, detail="Upload lecture files before asking questions.")

    history = [{"role": role, "content": content} for role, content in get_recent_messages(payload.sessionId, limit=5)]
    save_message(payload.sessionId, "user", payload.question)
    answer = rag.answer_question(payload.sessionId, payload.question, history=history)
    save_message(payload.sessionId, "assistant", answer)
    return {"answer": answer}


@app.post("/api/test-questions")
def generate_test_questions(payload: StudyTopicRequest):
    if not payload.topic.strip():
        raise HTTPException(status_code=400, detail="Please enter a topic to study.")

    if not rag.get_session_documents(payload.sessionId):
        raise HTTPException(status_code=400, detail="Upload lecture files before generating study questions.")

    questions = rag.generate_study_questions(payload.sessionId, payload.topic)
    return {"questions": questions}


if frontend_dist.exists():
    @app.get("/")
    def serve_index():
        return FileResponse(frontend_dist / "index.html")

    @app.get("{full_path:path}")
    def serve_spa(full_path: str):
        if full_path.startswith("api/"):
            raise HTTPException(status_code=404)
        file_path = frontend_dist / full_path
        if file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(frontend_dist / "index.html")
