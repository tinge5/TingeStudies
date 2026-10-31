import os
from pathlib import Path
from typing import Dict, List

import faiss
import numpy as np
from docx import Document
from openai import OpenAI
from pptx import Presentation
from pypdf import PdfReader

from app.config import ALLOWED_EXTENSIONS, OPENAI_API_KEY, get_chat_model_name

APP_STORAGE_DIR = Path(__file__).resolve().parents[1] / "uploads"
APP_STORAGE_DIR.mkdir(parents=True, exist_ok=True)


def extract_text_from_file(file_path: Path) -> str:
    suffix = file_path.suffix.lower()
    if suffix == ".pdf":
        reader = PdfReader(str(file_path))
        pages = []
        for page in reader.pages:
            text = page.extract_text() or ""
            pages.append(text)
        return "\n\n".join(pages)

    if suffix == ".docx":
        doc = Document(str(file_path))
        paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
        return "\n".join(paragraphs)

    if suffix == ".pptx":
        presentation = Presentation(str(file_path))
        slides = []
        for slide in presentation.slides:
            texts = []
            for shape in slide.shapes:
                if hasattr(shape, "text") and shape.text:
                    texts.append(shape.text.strip())
            if texts:
                slides.append("\n".join(texts))
        return "\n\n".join(slides)

    raise ValueError(f"Unsupported file type: {suffix}")


def chunk_text(text: str, chunk_size: int = 700) -> List[str]:
    if not text.strip():
        return []

    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks: List[str] = []
    current: List[str] = []
    current_length = 0

    for paragraph in paragraphs:
        if current_length + len(paragraph) > chunk_size and current:
            chunks.append("\n".join(current))
            current = [paragraph]
            current_length = len(paragraph)
        else:
            current.append(paragraph)
            current_length += len(paragraph)

    if current:
        chunks.append("\n".join(current))

    return chunks


class StudyRAG:
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None
        self.session_docs: Dict[str, List[dict]] = {}

    def process_upload(self, session_id: str, file_path: Path, original_name: str) -> dict:
        if file_path.suffix.lower() not in ALLOWED_EXTENSIONS:
            raise ValueError(f"File type is not allowed: {original_name}")

        text = extract_text_from_file(file_path)
        chunks = chunk_text(text)
        if not chunks:
            raise ValueError(f"No readable text found in {original_name}")

        entry = {
            "file_name": original_name,
            "file_path": str(file_path),
            "chunks": chunks,
        }

        self.session_docs.setdefault(session_id, []).append(entry)
        return {"fileName": original_name, "chunks": len(chunks)}

    def get_session_documents(self, session_id: str) -> List[str]:
        docs = self.session_docs.get(session_id, [])
        text_chunks = []
        for doc in docs:
            text_chunks.extend(doc["chunks"])
        return text_chunks

    def _embed(self, texts: List[str]) -> np.ndarray:
        if not self.client:
            raise ValueError("OPENAI_API_KEY is not configured.")

        response = self.client.embeddings.create(
            model="text-embedding-3-small",
            input=texts,
        )
        return np.array([item.embedding for item in response.data], dtype="float32")

    def answer_question(self, session_id: str, question: str, history: list[dict] | None = None) -> str:
        if not self.client:
            raise ValueError("OPENAI_API_KEY is not configured.")

        docs = self.get_session_documents(session_id)
        if not docs:
            return "Please upload lecture files before asking questions."

        question_embedding = self._embed([question])[0]
        doc_embeddings = self._embed(docs)

        index = faiss.IndexFlatL2(doc_embeddings.shape[1])
        index.add(doc_embeddings)
        distances, indices = index.search(np.asarray([question_embedding], dtype="float32"), k=min(4, len(docs)))

        context_chunks = [docs[idx] for idx in indices[0] if idx < len(docs)]
        context_text = "\n\n".join(context_chunks)

        prompt = (
            "You are a study tutor. Answer briefly using only the uploaded lecture content below. "
            "Keep the response to 2-4 sentences unless the user asks for more detail. "
            "If the answer is not clearly supported by the uploaded materials, say that it is not in the provided files. "
            "Do not use outside knowledge or web sources.\n\n"
            f"Context from uploaded files:\n{context_text}\n\nQuestion: {question}"
        )

        messages = [
            {"role": "system", "content": "You are a factual study assistant that answers briefly and only from the uploaded course materials."},
        ]
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": prompt})

        completion = self.client.chat.completions.create(
            model=get_chat_model_name(),
            messages=messages,
            temperature=0.2,
            max_completion_tokens=350,
        )
        return completion.choices[0].message.content.strip()

    def generate_study_questions(self, session_id: str, topic: str) -> str:
        if not self.client:
            raise ValueError("OPENAI_API_KEY is not configured.")

        docs = self.get_session_documents(session_id)
        if not docs:
            return "Please upload lecture files before generating study questions."

        context_text = "\n\n".join(docs[:10])
        prompt = (
            "Create 5 concise study questions based only on the uploaded lecture content below. "
            "Focus on the requested topic: {topic}. Return only a numbered list.\n\n"
            f"Context:\n{context_text}"
        ).format(topic=topic)

        completion = self.client.chat.completions.create(
            model=get_chat_model_name(),
            messages=[
                {"role": "system", "content": "Generate brief practice questions only from the uploaded material."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.4,
            max_completion_tokens=350,
        )
        return completion.choices[0].message.content.strip()
