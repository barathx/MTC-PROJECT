"""Test the upgraded OCR pipeline on an existing MTC PDF."""
from ai_pipeline.pdf_processor import pdf_to_images
from ai_pipeline.preprocessor import preprocess_image
from ai_pipeline.ocr_engine import extract_text_from_image, extract_tables_from_image
from ai_pipeline.extractor import extract_structured_data
import json

print("=== Testing OCR Pipeline on MTC PDF ===")
images = pdf_to_images("c:/Users/rblov/OneDrive/Desktop/MTC/uploads/081b6b4a4be8472cab6506c0f59d3631.pdf")
print(f"Pages converted: {len(images)}")

if images:
    img = images[0]
    processed = preprocess_image(img)
    print("Preprocessing done.")

    print("\n--- OCR Text Extraction ---")
    text = extract_text_from_image(processed)
    print(f"OCR text length: {len(text)} chars")
    print(text[:500])

    print("\n--- Table Extraction ---")
    tables = extract_tables_from_image(img)
    print(f"Tables found: {len(tables)}")
    for i, t in enumerate(tables):
        ttype = t.get("type", "unknown")
        has_res = "res" in t
        print(f"  Region {i}: type={ttype}, has_res={has_res}")

    print("\n--- Structured Data Extraction ---")
    data = extract_structured_data(text, table_data=tables)
    print(json.dumps(data, indent=2, default=str))
else:
    print("ERROR: No images from PDF.")
