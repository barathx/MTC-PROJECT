import sys
import os
from sqlalchemy.orm import Session

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from database import SessionLocal
from models import Document
from ai_pipeline.pdf_processor import pdf_to_images
from ai_pipeline.ocr_engine import extract_text_from_images
from ai_pipeline.preprocessor import preprocess_image

def debug_latest():
    db = SessionLocal()
    try:
        doc = db.query(Document).order_by(Document.uploaded_at.desc()).first()
        if not doc:
            print("No documents found.")
            return
            
        print(f"DEBUGGING DOC: {doc.id} - {doc.filename}")
        print(f"PATH: {doc.file_path}")
        
        # Run OCR
        images = pdf_to_images(doc.file_path)
        processed = [preprocess_image(img) for img in images]
        raw_text = extract_text_from_images(processed)
        
        print("\n--- RAW OCR TEXT START ---")
        print(raw_text)
        print("--- RAW OCR TEXT END ---")
        
        with open("debug_mtc_sample_ocr.txt", "w", encoding="utf-8") as f:
            f.write(raw_text)
            
    finally:
        db.close()

if __name__ == "__main__":
    debug_latest()
