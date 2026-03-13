import os
import subprocess
import asyncio
import sys
from PIL import Image

try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False

# Lazy initialization of PaddleOCR
_paddle_ocr = None

def get_paddle_ocr():
    global _paddle_ocr
    if _paddle_ocr is None:
        from paddleocr import PaddleOCR
        # Minimal arguments for broadest compatibility
        _paddle_ocr = PaddleOCR(use_angle_cls=True, lang='en')
    return _paddle_ocr

def extract_text_from_image(image: Image.Image) -> str:
    """
    Extract text from a PIL Image.
    Primary: PaddleOCR (Highest accuracy for MTC scans)
    Fallback: Windows Native OCR (winsdk)
    Fallback 2: Tesseract
    """
    # 0. Save temp image for external tools
    temp_path = os.path.join(os.getcwd(), "temp_ocr_image.png")
    image.save(temp_path)

    # 1. Try PaddleOCR (Recommended by Step 1)
    try:
        print("Running PaddleOCR...")
        import numpy as np
        ocr = get_paddle_ocr()
        
        # Convert PIL to numpy (RGB to BGR as Paddle expects BGR)
        img_np = np.array(image.convert('RGB'))
        img_np = img_np[:, :, ::-1].copy() # RGB to BGR
        
        result = ocr.ocr(img_np)
        if result and result[0]:
            lines = [line[1][0] for line in result[0]]
            text = "\n".join(lines)
            if text.strip():
                print("PaddleOCR successful.")
                return text.strip()
    except Exception as e:
        print(f"PaddleOCR failed: {e}")

    # 2. Try Windows Native OCR (via our winsdk script)
    if os.name == 'nt':
        try:
            native_ocr_script = os.path.join(os.path.dirname(__file__), "native_ocr.py")
            cmd = [sys.executable, native_ocr_script, temp_path]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0 and result.stdout.strip():
                if "OCR_ERROR" not in result.stdout:
                    print("Windows Native OCR (winsdk) successful.")
                    return result.stdout.strip()
            print(f"Windows Native OCR failed or empty. Output: {result.stdout}")
        except Exception as e:
            print(f"Windows Native OCR error: {e}")

    # 3. Try Tesseract
    if TESSERACT_AVAILABLE:
        try:
            print("Trying Tesseract OCR...")
            text = pytesseract.image_to_string(image, config=r'--oem 3 --psm 6')
            if text.strip() and len(text.strip()) > 10:
                print("Tesseract OCR successful.")
                return text.strip()
        except Exception as e:
            print(f"Tesseract failed: {e}")

    return "[OCR Error: Extraction failed. Please ensure OCR engines are working or use a text-based PDF.]"


def extract_text_from_images(images: list[Image.Image]) -> str:
    """Extract and combine text from multiple images."""
    all_text = []
    for i, img in enumerate(images):
        text = extract_text_from_image(img)
        if text:
            all_text.append(f"--- Page {i + 1} ---\n{text}")
    return "\n\n".join(all_text)
