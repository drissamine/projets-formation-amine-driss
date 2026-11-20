"""Quick test for PaddleOCR."""

import sys
import cv2
from pathlib import Path

BASE_DIR = Path(__file__).parent


def test_paddleocr(image_path: str = None):
    """Test PaddleOCR on an image."""
    print("=" * 60)
    print("Testing PaddleOCR")
    print("=" * 60)

    try:
        from paddleocr import PaddleOCR
    except ImportError:
        print("\nERROR: PaddleOCR not installed!")
        print("Run: pip install paddlepaddle paddleocr")
        return

    print("\nInitializing PaddleOCR (first run may download models)...")

    ocr = PaddleOCR(use_angle_cls=True, lang="fr", use_gpu=False, show_log=False)

    print("PaddleOCR ready!\n")

    if not image_path:
        test_images = [
            BASE_DIR
            / "dataset"
            / "images"
            / "driver_license"
            / "permis-de-conduire-fr.png",
            BASE_DIR / "dataset" / "images" / "id_card" / "id_card_000.jpg",
            BASE_DIR / "dataset" / "images" / "passport" / "passport_000.jpg",
        ]

        for img in test_images:
            if img.exists():
                image_path = str(img)
                break

    if not image_path:
        print("No test image found!")
        return

    print(f"Testing on: {image_path}\n")

    import time

    start = time.time()

    result = ocr.ocr(image_path, cls=True)

    elapsed = time.time() - start
    print(f"Processing time: {elapsed:.2f}s\n")

    if result and result[0]:
        print(f"Found {len(result[0])} text regions:\n")

        all_text = ""
        for i, line in enumerate(result[0], 1):
            text = line[1][0]
            conf = line[1][1]
            all_text += text + " "
            print(f"  {i}. [{conf:.2f}] {text}")

        print(f"\n--- Full Text ---")
        print(all_text[:500])

    else:
        print("No text detected!")

    print("\n" + "=" * 60)
    print("Test completed!")
    print("=" * 60)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        test_paddleocr(sys.argv[1])
    else:
        test_paddleocr()
