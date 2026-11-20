"""Simple OCR fix for real photos - minimal preprocessing."""

import cv2
import numpy as np
from PIL import Image
import pytesseract
from pathlib import Path
import sys


def simple_preprocess(image_path: str) -> np.ndarray:
    """
    Minimal preprocessing that works for most cases.
    """
    # Load
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Cannot load image: {image_path}")

    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Get current size
    h, w = gray.shape
    print(f"Original size: {w}x{h}")

    # UPSCALE if too small (critical for Tesseract)
    if w < 1000:
        # Scale up to at least 1500px width
        scale = 1500 / w
        new_w = int(w * scale)
        new_h = int(h * scale)
        gray = cv2.resize(gray, (new_w, new_h), interpolation=cv2.INTER_CUBIC)
        print(f"Resized to: {new_w}x{new_h}")

    # Simple threshold - works better than adaptive for clean documents
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    return binary


def denoise_preprocess(image_path: str) -> np.ndarray:
    """
    For noisy photos (taken with phone in poor light).
    """
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    h, w = gray.shape

    # Upscale
    if w < 1000:
        scale = 1500 / w
        gray = cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)

    # Denoise
    gray = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)

    # Enhance contrast
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    gray = clahe.apply(gray)

    # Threshold
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    return binary


def test_ocr(image_path: str):
    """Test OCR with different methods."""
    path = Path(image_path)
    if not path.exists():
        print(f"Error: File not found: {image_path}")
        return

    print(f"\n{'=' * 60}")
    print(f"Testing OCR on: {path.name}")
    print("=" * 60)

    # Output directory
    output_dir = Path("ocr_test_output")
    output_dir.mkdir(exist_ok=True)

    # Method 1: Simple (just resize + threshold)
    print("\n[1] Testing: Simple preprocessing")
    processed1 = simple_preprocess(image_path)
    cv2.imwrite(str(output_dir / f"{path.stem}_method1.jpg"), processed1)

    pil1 = Image.fromarray(processed1)
    text1 = pytesseract.image_to_string(pil1, lang="fra+eng")

    print(f"Result:\n{text1[:500]}...")

    # Method 2: With denoising
    print("\n[2] Testing: With denoising")
    try:
        processed2 = denoise_preprocess(image_path)
        cv2.imwrite(str(output_dir / f"{path.stem}_method2.jpg"), processed2)

        pil2 = Image.fromarray(processed2)
        text2 = pytesseract.image_to_string(pil2, lang="fra+eng")

        print(f"Result:\n{text2[:500]}...")
    except Exception as e:
        print(f"Error: {e}")

    # Method 3: Try EasyOCR if available
    print("\n[3] Testing: EasyOCR (if available)")
    try:
        import easyocr

        reader = easyocr.Reader(["fr", "en"], gpu=False)

        # EasyOCR works better on color images
        image = cv2.imread(image_path)
        results = reader.readtext(image)

        text3 = "\n".join([r[1] for r in results])
        print(f"Result:\n{text3[:500]}...")

    except ImportError:
        print("EasyOCR not installed. Run: pip install easyocr")
    except Exception as e:
        print(f"EasyOCR error: {e}")

    print(f"\n{'=' * 60}")
    print(f"Processed images saved to: {output_dir}")
    print("=" * 60)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        test_ocr(sys.argv[1])
    else:
        # Test with default images
        test_files = [
            "dataset/images/driver_license/permis-de-conduire-fr.png",
            "dataset/images/id_card/id_card_000.jpg",
        ]

        base = Path(__file__).parent
        for f in test_files:
            full = base / f
            if full.exists():
                test_ocr(str(full))
                break
        else:
            print("Usage: python fix_ocr_simple.py <image_path>")
