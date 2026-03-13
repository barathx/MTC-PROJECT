from paddleocr import PaddleOCR
import cv2
import numpy as np
import os
from PIL import Image

def test():
    print("Initializing PaddleOCR...")
    ocr = PaddleOCR(use_angle_cls=True, lang='en')
    
    # Create a dummy image
    img = np.zeros((100, 300, 3), dtype=np.uint8)
    cv2.putText(img, "TEST OCR", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    cv2.imwrite("test_paddle_input.png", img)
    
    print("\n1. Testing with FILE PATH...")
    try:
        result = ocr.ocr("test_paddle_input.png")
        print("Success!")
    except Exception as e:
        print(f"FAILED: {e}")

    print("\n2. Testing with NUMPY ARRAY (cv2)...")
    try:
        img_cv2 = cv2.imread("test_paddle_input.png")
        result = ocr.ocr(img_cv2)
        print("Success!")
    except Exception as e:
        print(f"FAILED: {e}")

    print("\n3. Testing with NUMPY ARRAY (PIL)...")
    try:
        img_pil = Image.open("test_paddle_input.png").convert('RGB')
        img_np = np.array(img_pil)
        # Paddle expects BGR
        img_np = img_np[:, :, ::-1].copy()
        result = ocr.ocr(img_np)
        print("Success!")
    except Exception as e:
        print(f"FAILED: {e}")

if __name__ == "__main__":
    test()
