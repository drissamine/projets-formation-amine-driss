"""Test with EasyOCR only - better for phone photos."""

import cv2
import sys
from pathlib import Path


def test_with_easyocr(image_path: str):
    """Test OCR using EasyOCR (handles phone photos better)."""
    print(f"\n{'=' * 60}")
    print(f"Testing EasyOCR on: {image_path}")
    print("=" * 60)

    path = Path(image_path)
    if not path.exists():
        print(f"[ERROR] File not found: {image_path}")
        return

    try:
        import easyocr
    except ImportError:
        print("[ERROR] EasyOCR not installed")
        print("Run: pip install easyocr")
        return

    # Initialize reader (CPU mode)
    print("Initializing EasyOCR (this may take a moment)...")
    reader = easyocr.Reader(["fr", "en"], gpu=False, verbose=False)
    print("Ready!")

    # Load image
    image = cv2.imread(str(path))
    if image is None:
        print("[ERROR] Cannot read image")
        return

    print(f"Image size: {image.shape}")

    # Test 1: Original image
    print("\n[1] Testing on original image...")
    results1 = reader.readtext(image, detail=1)

    text1 = "\n".join([r[1] for r in results1])
    avg_conf1 = sum([r[2] for r in results1]) / len(results1) if results1 else 0

    print(f"Confidence: {avg_conf1:.2f}")
    print(f"Text:\n{text1[:800]}...")

    # Test 2: Upscaled image (EasyOCR also benefits from larger images)
    print("\n[2] Testing on upscaled image (2x)...")
    h, w = image.shape[:2]
    upscaled = cv2.resize(image, (w * 2, h * 2), interpolation=cv2.INTER_CUBIC)

    results2 = reader.readtext(upscaled, detail=1)
    text2 = "\n".join([r[1] for r in results2])
    avg_conf2 = sum([r[2] for r in results2]) / len(results2) if results2 else 0

    print(f"Confidence: {avg_conf2:.2f}")
    print(f"Text:\n{text2[:800]}...")

    # Summary
    print(f"\n{'=' * 60}")
    print("SUMMARY")
    print("=" * 60)
    print(f"Original: {len(text1)} chars, confidence {avg_conf1:.2f}")
    print(f"Upscaled: {len(text2)} chars, confidence {avg_conf2:.2f}")

    if avg_conf2 > avg_conf1:
        print("\n[BEST] Upscaled image gives better results")
    else:
        print("\n[BEST] Original image is fine")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        test_with_easyocr(sys.argv[1])
    else:
        # Test default images
        base = Path(__file__).parent
        test_files = [
            base
            / "dataset"
            / "images"
            / "driver_license"
            / "permis-de-conduire-fr.png",
            base / "dataset" / "images" / "id_card" / "id_card_000.jpg",
            base / "dataset" / "images" / "passport" / "passport_000.jpg",
        ]

        for f in test_files:
            if f.exists():
                test_with_easyocr(str(f))
                break
        else:
            print("Usage: python test_easyocr_only.py <image_path>")
