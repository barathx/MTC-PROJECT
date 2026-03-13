"""Image preprocessing for better OCR accuracy."""
import numpy as np
from PIL import Image, ImageFilter, ImageEnhance

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False


def preprocess_image(image: Image.Image) -> Image.Image:
    """
    Preprocess an image for better OCR results.
    Uses OpenCV if available, falls back to Pillow.
    """
    if CV2_AVAILABLE:
        return _preprocess_with_cv2(image)
    else:
        return _preprocess_with_pillow(image)


def _preprocess_with_cv2(image: Image.Image) -> Image.Image:
    """Simplified OpenCV-based preprocessing (Grayscale + Contrast)."""
    img_array = np.array(image)

    # Convert to grayscale
    if len(img_array.shape) == 3:
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
    else:
        gray = img_array

    # Enhance contrast using CLAHE (Contrast Limited Adaptive Histogram Equalization)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)

    return Image.fromarray(enhanced)


def _preprocess_with_pillow(image: Image.Image) -> Image.Image:
    """Pillow-based preprocessing fallback."""
    # Convert to grayscale
    img = image.convert("L")

    # Enhance contrast
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(2.0)

    # Enhance sharpness
    enhancer = ImageEnhance.Sharpness(img)
    img = enhancer.enhance(2.0)

    # Apply slight blur to reduce noise, then sharpen
    img = img.filter(ImageFilter.MedianFilter(size=3))
    img = img.filter(ImageFilter.SHARPEN)

    return img
