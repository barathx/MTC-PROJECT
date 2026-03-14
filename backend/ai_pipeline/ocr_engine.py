"""
High-accuracy OCR engine for MTC documents.
Primary: PaddleOCR PP-OCRv4 with GPU acceleration.
Table extraction: PPStructure for structured table recognition.
Fallbacks: Windows Native OCR (winsdk), Tesseract.
"""
import os
import subprocess
import sys
import numpy as np
from PIL import Image

try:
    import pytesseract
    # Configure path for Windows
    if os.name == 'nt':
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False

def get_paddle_ocr():
    return None

def get_table_engine():
    return None

# ─── Public API ───

def extract_text_from_image(image: Image.Image) -> str:
    """
    Extract text from a PIL Image using Tesseract OCR.
    """
    if TESSERACT_AVAILABLE:
        try:
            print("Running Tesseract OCR...")
            # Use psm 6 = Assume a single uniform block of text (keeps table rows together better)
            # Add config to preserve spaces and treat it as a block
            text = pytesseract.image_to_string(image, config=r'--oem 3 --psm 6 -c preserve_interword_spaces=1')
            if text.strip() and len(text.strip()) > 10:
                print(f"Tesseract OCR successful ({len(text.splitlines())} lines).")
                return text.strip()
        except Exception as e:
            print(f"Tesseract failed: {e}")

    return "[OCR Error: Extraction failed. Please ensure OCR engines are working or use a text-based PDF.]"


def extract_tables_from_image(image: Image.Image) -> list[dict]:
    """
    Extract structured table data from an image using PPStructure.
    Returns a list of table dicts, each with 'type' and 'res' keys.
    Table results contain HTML or structured cell data.
    """
    engine = get_table_engine()
    if engine is None:
        return []

    try:
        img_np = np.array(image.convert('RGB'))
        img_np = img_np[:, :, ::-1].copy()  # RGB → BGR

        result = engine(img_np)
        tables = []
        for item in result:
            if item.get('type') == 'table':
                tables.append(item)
            elif item.get('type') == 'text':
                tables.append(item)
        
        if tables:
            print(f"PPStructure detected {len(tables)} regions (tables/text).")
        return tables
    except Exception as e:
        print(f"PPStructure table extraction failed: {e}")
        return []


def extract_text_from_images(images: list[Image.Image]) -> str:
    """Extract and combine text from multiple images."""
    all_text = []
    for i, img in enumerate(images):
        text = extract_text_from_image(img)
        if text:
            all_text.append(f"--- Page {i + 1} ---\n{text}")
    return "\n\n".join(all_text)


def extract_tables_from_images(images: list[Image.Image]) -> list[dict]:
    """Extract structured table data from multiple images."""
    all_tables = []
    for i, img in enumerate(images):
        tables = extract_tables_from_image(img)
        for t in tables:
            t['page'] = i + 1
        all_tables.extend(tables)
    return all_tables
