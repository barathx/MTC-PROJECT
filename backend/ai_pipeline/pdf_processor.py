import fitz  # PyMuPDF
from pathlib import Path
from PIL import Image
try:
    from pdf2image import convert_from_path
    PDF2IMAGE_AVAILABLE = True
except ImportError:
    PDF2IMAGE_AVAILABLE = False


def pdf_to_images(pdf_path: str, dpi: int = 300) -> list[Image.Image]:
    """
    Convert a PDF file to a list of PIL Images (one per page).
    Uses PyMuPDF (fitz) as primary because it doesn't require poppler.
    """
    try:
        doc = fitz.open(pdf_path)
        images = []
        for page in doc:
            # Render page to a pixmap
            pix = page.get_pixmap(matrix=fitz.Matrix(dpi/72, dpi/72))
            # Convert pixmap to PIL Image
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            images.append(img)
        doc.close()
        if images:
            return images
    except Exception as e:
        print(f"PyMuPDF conversion failed: {e}")

    # Fallback to pdf2image if available
    if PDF2IMAGE_AVAILABLE:
        try:
            return convert_from_path(pdf_path, dpi=dpi)
        except Exception as e:
            print(f"pdf2image conversion failed: {e}")

    return []


def is_pdf(file_path: str) -> bool:
    """Check if a file is a PDF."""
    return Path(file_path).suffix.lower() == ".pdf"

def extract_native_text(pdf_path: str) -> str:
    """
    Extracts embedded text directly from a PDF.
    Returns the string text or empty string if it's a scanned/flattened image PDF.
    """
    try:
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text() + "\n"
        doc.close()
        return text.strip()
    except Exception as e:
        print(f"PyMuPDF native text extraction failed: {e}")
        return ""
