import sys
import os
from PIL import Image
import numpy as np

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from ai_pipeline.pdf_processor import pdf_to_images
from ai_pipeline.ocr_engine import extract_text_from_images
from ai_pipeline.preprocessor import preprocess_image

def test_ocr_variants():
    pdf_path = r"c:\Users\rblov\OneDrive\Desktop\MTC\uploads\da8d03884654422196bfc6cf703e24ef.pdf"
    
    # 1. PDF to Images
    images = pdf_to_images(pdf_path)
    if not images:
        print("Failed to load images.")
        return
        
    img = images[0]
    
    print("\n--- VARIANT 1: RAW IMAGE ---")
    raw_text = extract_text_from_images([img])
    print(raw_text[:200] + "...")
    
    print("\n--- VARIANT 2: PREPROCESSED IMAGE ---")
    proc_img = preprocess_image(img)
    proc_text = extract_text_from_images([proc_img])
    print(proc_text[:200] + "...")
    
    with open("ocr_comparison.txt", "w", encoding="utf-8") as f:
        f.write("RAW TEXT:\n")
        f.write(raw_text)
        f.write("\n\nPREPROCESSED TEXT:\n")
        f.write(proc_text)

if __name__ == "__main__":
    test_ocr_variants()
