import sys
import os
from PIL import Image
from sqlalchemy.orm import Session

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from ai_pipeline.pdf_processor import pdf_to_images
from ai_pipeline.ocr_engine import extract_text_from_images
from ai_pipeline.extractor import extract_structured_data
from ai_pipeline.preprocessor import preprocess_image

def test_full_pipeline():
    pdf_path = r"c:\Users\rblov\OneDrive\Desktop\MTC\uploads\5fa21e1d2413412eaaf1e4c4ec14ae79.pdf"
    
    # 1. PDF to Images
    images = pdf_to_images(pdf_path)
    
    # 2. Preprocess & OCR
    processed = [preprocess_image(img) for img in images]
    raw_text = extract_text_from_images(processed)
    
    print("\n--- FULL RAW OCR TEXT ---")
    print(raw_text)
    print("--- END FULL RAW OCR TEXT ---")
    
    with open("raw_ocr_dump.txt", "w", encoding="utf-8") as f:
        f.write(raw_text)

if __name__ == "__main__":
    test_full_pipeline()
