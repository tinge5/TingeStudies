import os
from pathlib import Path

from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parents[2]
load_dotenv(ROOT_DIR / ".env")

ALLOWED_EXTENSIONS = {
    ".pdf": "application/pdf",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
}
ALLOWED_FILE_TYPES = set(ALLOWED_EXTENSIONS.values())

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "openai/gpt-5.4-mini")


def get_chat_model_name() -> str:
    model_name = OPENAI_MODEL.strip()
    return model_name.replace("openai/", "", 1) if model_name.startswith("openai/") else model_name
