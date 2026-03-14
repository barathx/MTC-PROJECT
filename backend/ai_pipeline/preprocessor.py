"""
Advanced image preprocessing for high-accuracy OCR on MTC documents.
Includes deskewing, denoising, adaptive thresholding, and upscaling.
"""
import numpy as np
from PIL import Image, ImageFilter, ImageEnhance

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False


# Minimum width for reliable OCR (equivalent to ~300 DPI on A4)
MIN_WIDTH = 2400


def preprocess_image(image: Image.Image) -> Image.Image:
    """
    Preprocess an image for high-accuracy OCR results.
    Pipeline: Upscale → Deskew → Denoise → Adaptive Threshold → Contrast.
    Uses OpenCV if available, falls back to Pillow.
    """
    if CV2_AVAILABLE:
        return _preprocess_with_cv2(image)
    else:
        return _preprocess_with_pillow(image)


def _preprocess_with_cv2(image: Image.Image) -> Image.Image:
    """Full OpenCV preprocessing pipeline for MTC scans."""
    img_array = np.array(image)

    # 1. Upscale small images for better OCR accuracy
    img_array = _upscale(img_array)

    # 2. Convert to grayscale
    if len(img_array.shape) == 3:
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
    else:
        gray = img_array

    # 3. Deskew (straighten rotated scans)
    gray = _deskew(gray)

    # 4. Denoise (remove scan artifacts/noise)
    denoised = cv2.fastNlMeansDenoising(gray, h=12, templateWindowSize=7, searchWindowSize=21)

    # 5. Adaptive thresholding for better text/background separation
    # Use Gaussian adaptive threshold for uneven lighting in scans. This keeps text intact better than hard thresholding.
    thresh = cv2.adaptiveThreshold(
        denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY, blockSize=31, C=10
    )

    # 6. Morphological cleanup — just a very light touch to avoid destroying numbers
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 1))
    cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

    # 7. CLAHE for balanced contrast on the cleaned image
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    # Apply CLAHE on denoised (not threshold) for PaddleOCR which prefers grayscale
    enhanced_gray = clahe.apply(denoised)

    # Return the enhanced grayscale (PaddleOCR handles binarization internally)
    # But also store the thresholded version for Tesseract fallback
    result = Image.fromarray(enhanced_gray)
    result.info["thresholded"] = Image.fromarray(cleaned)
    return result


def _upscale(img_array: np.ndarray) -> np.ndarray:
    """Upscale small images to improve OCR accuracy."""
    h, w = img_array.shape[:2]
    if w < MIN_WIDTH:
        scale = MIN_WIDTH / w
        new_w = int(w * scale)
        new_h = int(h * scale)
        img_array = cv2.resize(img_array, (new_w, new_h), interpolation=cv2.INTER_CUBIC)
        print(f"Upscaled image from {w}x{h} to {new_w}x{new_h}")
    return img_array


def _deskew(gray: np.ndarray) -> np.ndarray:
    """Deskew a grayscale image by detecting text line angle."""
    try:
        # Use Canny edge detection + Hough lines to find dominant angle
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=100,
                                minLineLength=gray.shape[1] // 4, maxLineGap=10)
        if lines is not None and len(lines) > 0:
            angles = []
            for line in lines:
                x1, y1, x2, y2 = line[0]
                angle = np.degrees(np.arctan2(y2 - y1, x2 - x1))
                # Only consider near-horizontal lines (text lines)
                if abs(angle) < 10:
                    angles.append(angle)

            if angles:
                median_angle = np.median(angles)
                # Only deskew if angle is significant but not too large
                if 0.3 < abs(median_angle) < 8:
                    h, w = gray.shape
                    center = (w // 2, h // 2)
                    M = cv2.getRotationMatrix2D(center, median_angle, 1.0)
                    rotated = cv2.warpAffine(gray, M, (w, h),
                                             flags=cv2.INTER_CUBIC,
                                             borderMode=cv2.BORDER_REPLICATE)
                    print(f"Deskewed by {median_angle:.2f}°")
                    return rotated
    except Exception as e:
        print(f"Deskew failed (non-critical): {e}")

    return gray


def _preprocess_with_pillow(image: Image.Image) -> Image.Image:
    """Pillow-based preprocessing fallback."""
    # Convert to grayscale
    img = image.convert("L")

    # Upscale if needed
    if img.width < MIN_WIDTH:
        scale = MIN_WIDTH / img.width
        new_size = (int(img.width * scale), int(img.height * scale))
        img = img.resize(new_size, Image.BICUBIC)

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
