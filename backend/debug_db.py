from database import SessionLocal
from models import Document, ExtractedData
import os

def debug():
    db = SessionLocal()
    try:
        doc = db.query(Document).order_by(Document.uploaded_at.desc()).first()
        if not doc:
            print("No documents found in DB.")
            return

        print(f"DOCUMENT ID: {doc.id}")
        print(f"FILENAME: {doc.filename}")
        print(f"STATUS: {doc.status}")
        
        ext = db.query(ExtractedData).filter(ExtractedData.document_id == doc.id).first()
        if not ext:
            print("No ExtractedData record found for this document.")
            return
            
        print("\n--- RAW TEXT START ---")
        print(ext.raw_text)
        print("--- RAW TEXT END ---")
        
        print("\n--- EXTRACTED FIELDS ---")
        print(f"Carbon: {ext.carbon}")
        print(f"Manganese: {ext.manganese}")
        print(f"Grade: {ext.material_grade}")
        print(f"Heat No: {ext.heat_number}")
        
    finally:
        db.close()

if __name__ == "__main__":
    debug()
