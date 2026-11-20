"""Test OCR with Tesseract only (faster)."""

import sys
import cv2
import numpy as np
from pathlib import Path
from PIL import Image

BASE_DIR = Path(__file__).parent


def preprocess_v1_simple(image_bgr):
    """Simple but effective preprocessing."""
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape

    # Upscale small images (Tesseract works better at 300+ DPI)
    if w < 1000:
        scale = 1500 / w
        resized = cv2.resize(
            gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC
        )
    else:
        resized = gray

    # Otsu threshold - works well for high contrast documents
    _, binary = cv2.threshold(resized, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    return binary


def preprocess_v2_denoise(image_bgr):
    """With denoising for photos."""
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)

    # Denoise
    denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)

    # Upscale
    h, w = denoised.shape
    if w < 1000:
        scale = 1500 / w
        denoised = cv2.resize(
            denoised, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC
        )

    # CLAHE for contrast
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(denoised)

    # Threshold
    _, binary = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    return binary


def preprocess_v3_adaptive(image_bgr):
    """Adaptive threshold for uneven lighting."""
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)

    # Resize
    h, w = gray.shape
    if w < 1000:
        scale = 1500 / w
        gray = cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)

    # Adaptive threshold
    binary = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
    )

    return binary


def test_tesseract(image_path: str):
    """Test with Tesseract only."""
    print(f"\n{'=' * 70}")
    print(f"Testing Tesseract OCR on: {image_path}")
    print("=" * 70)

    try:
        import pytesseract
    except ImportError:
        print("[ERROR] pytesseract not installed")
        return

    path = Path(image_path)
    if not path.exists():
        print(f"[ERROR] File not found: {image_path}")
        return

    # Load
    image = cv2.imread(str(path))
    if image is None:
        print("[ERROR] Cannot read image")
        return

    print(f"Original size: {image.shape}")

    # Output dir
    output_dir = BASE_DIR / "ocr_tesseract_results"
    output_dir.mkdir(exist_ok=True)

    methods = [
        ("Original grayscale", lambda img: cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)),
        ("Simple (resize + Otsu)", preprocess_v1_simple),
        ("Denoise + CLAHE", preprocess_v2_denoise),
        ("Adaptive threshold", preprocess_v3_adaptive),
    ]

    best_result = None
    best_conf = 0

    for i, (name, func) in enumerate(methods, 1):
        print(f"\n{'-' * 70}")
        print(f"Method {i}: {name}")
        print("-" * 70)

        try:
            # Process
            processed = func(image)

            # Save
            out_path = output_dir / f"{path.stem}_method{i}.jpg"
            cv2.imwrite(str(out_path), processed)

            # OCR
            pil_img = Image.fromarray(processed)

            # Get text
            text = pytesseract.image_to_string(pil_img, lang="fra+eng")

            # Get confidence data
            data = pytesseract.image_to_data(
                pil_img, lang="fra+eng", output_type=pytesseract.Output.DICT
            )

            # Calculate confidence
            confs = [int(c) for c in data["conf"] if int(c) > 0]
            avg_conf = sum(confs) / len(confs) if confs else 0

            print(f"Confidence: {avg_conf:.1f}%")
            print(f"Text length: {len(text)} chars")
            print(f"\nExtracted text:\n{text[:500]}...")

            if avg_conf > best_conf:
                best_conf = avg_conf
                best_result = (name, text, avg_conf)

        except Exception as e:
            print(f"[ERROR] {e}")

    # Summary
    print(f"\n{'=' * 70}")
    print("BEST RESULT")
    print("=" * 70)
    if best_result:
        print(f"Method: {best_result[0]}")
        print(f"Confidence: {best_result[2]:.1f}%")
        print(f"\nFull text:\n{best_result[1]}")

    print(f"\nImages saved to: {output_dir}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        test_tesseract(sys.argv[1])
    else:
        # Default test
        test_files = [
            BASE_DIR
            / "dataset"
            / "images"
            / "driver_license"
            / "permis-de-conduire-fr.png",
            BASE_DIR / "dataset" / "images" / "id_card" / "id_card_000.jpg",
        ]

        for f in test_files:
            if f.exists():
                test_tesseract(str(f))
                break
        else:
            print("Usage: python test_tesseract_only.py <image_path>")
