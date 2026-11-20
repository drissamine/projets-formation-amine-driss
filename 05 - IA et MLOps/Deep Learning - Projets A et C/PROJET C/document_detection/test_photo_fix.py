"""Test OCR on real phone photos with aggressive preprocessing."""

import sys
import cv2
import numpy as np
from pathlib import Path

BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR / "src"))

from ocr.engine import OCREngine


def aggressive_preprocess(image_bgr: np.ndarray) -> dict:
    """Multiple preprocessing strategies for phone photos."""
    results = {}

    # Original grayscale
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)

    # Strategy 1: Simple resize + threshold (best for clean text)
    h, w = gray.shape
    if w < 1000:
        resized = cv2.resize(
            gray, (int(w * 2), int(h * 2)), interpolation=cv2.INTER_CUBIC
        )
    else:
        resized = gray
    _, thresh1 = cv2.threshold(resized, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    results["resize_otsu"] = thresh1

    # Strategy 2: Denoise + enhance
    denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(denoised)
    _, thresh2 = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    results["denoise_clahe"] = thresh2

    # Strategy 3: Adaptive threshold (better for uneven lighting)
    adaptive = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
    )
    results["adaptive"] = adaptive

    # Strategy 4: High contrast
    normalized = cv2.normalize(gray, None, 0, 255, cv2.NORM_MINMAX)
    _, thresh4 = cv2.threshold(normalized, 127, 255, cv2.THRESH_BINARY)
    results["normalized"] = thresh4

    # Strategy 5: Morphological operations (connect broken text)
    kernel = np.ones((2, 2), np.uint8)
    morph = cv2.morphologyEx(thresh1, cv2.MORPH_CLOSE, kernel)
    results["morphological"] = morph

    return results


def test_image(image_path: str):
    """Test OCR with multiple preprocessing methods."""
    print(f"\n{'=' * 70}")
    print(f"Testing: {image_path}")
    print("=" * 70)

    path = Path(image_path)
    if not path.exists():
        print(f"[ERROR] File not found")
        return

    # Load image
    image = cv2.imread(str(path))
    if image is None:
        print(f"[ERROR] Cannot read image")
        return

    print(f"Image size: {image.shape}")

    # Initialize OCR
    ocr = OCREngine()
    print(f"OCR Engines: {ocr.get_available_engines()}")

    # Create output directory
    output_dir = BASE_DIR / "ocr_debug"
    output_dir.mkdir(exist_ok=True)

    # Test original
    print(f"\n{'-' * 70}")
    print("Method 1: Original (grayscale only)")
    print("-" * 70)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    cv2.imwrite(str(output_dir / f"{path.stem}_1_original.jpg"), gray)
    text, conf = ocr.recognize(gray)
    print(f"Confidence: {conf:.2f}")
    print(f"Text: {text[:300]}...")

    # Test preprocessed versions
    print(f"\n{'-' * 70}")
    print("Generating preprocessed versions...")
    print("-" * 70)

    processed = aggressive_preprocess(image)

    best_text = ""
    best_conf = 0
    best_method = ""

    for i, (method_name, img) in enumerate(processed.items(), 2):
        # Save
        out_path = output_dir / f"{path.stem}_{i}_{method_name}.jpg"
        cv2.imwrite(str(out_path), img)

        # OCR
        text, conf = ocr.recognize(img)

        print(f"\n{method_name}:")
        print(f"  Confidence: {conf:.2f}")
        print(f"  Text preview: {text[:200]}...")

        if conf > best_conf:
            best_conf = conf
            best_text = text
            best_method = method_name

    # Summary
    print(f"\n{'=' * 70}")
    print("BEST RESULT")
    print("=" * 70)
    print(f"Method: {best_method}")
    print(f"Confidence: {best_conf:.2f}")
    print(f"\nFull text:\n{best_text}")
    print(f"\nSaved debug images to: {output_dir}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        test_image(sys.argv[1])
    else:
        # Test with available images
        test_files = [
            BASE_DIR
            / "dataset"
            / "images"
            / "driver_license"
            / "permis-de-conduire-fr.png",
            BASE_DIR / "dataset" / "images" / "id_card" / "id_card_000.jpg",
            BASE_DIR / "dataset" / "images" / "passport" / "passport_000.jpg",
        ]

        for f in test_files:
            if f.exists():
                test_image(str(f))
                break
        else:
            print("No test images found")
            print(f"Usage: python {sys.argv[0]} <image_path>")
