import uuid
import os
from pathlib import Path
from config import UPLOAD_DIR, ALLOWED_EXTENSIONS


def save_uploaded_file(file_content: bytes, original_filename: str) -> tuple[str, str]:
    """
    Save an uploaded file to the uploads directory.
    Returns (unique_filename, file_path).
    """
    ext = Path(original_filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(f"File type {ext} not supported. Allowed: {ALLOWED_EXTENSIONS}")

    unique_filename = f"{uuid.uuid4().hex}{ext}"
    file_path = UPLOAD_DIR / unique_filename

    with open(file_path, "wb") as f:
        f.write(file_content)

    return unique_filename, str(file_path)


def get_file_type(filename: str) -> str:
    """Determine file type from extension."""
    ext = Path(filename).suffix.lower()
    if ext == ".pdf":
        return "pdf"
    elif ext in {".png", ".jpg", ".jpeg", ".tiff", ".tif"}:
        return "image"
    return "unknown"
