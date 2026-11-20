"""Test DocTR OCR on document images."""

import sys
from pathlib import Path
from doctr.io import DocumentFile
from doctr.models import ocr_predictor
import time

BASE_DIR = Path(__file__).parent


def test_doctr(image_path: str = None):
    """Test DocTR on an image."""
    print("=" * 60)
    print("Testing DocTR OCR")
    print("=" * 60)

    print("\nLoading DocTR model (first run downloads models)...")
    model = ocr_predictor(pretrained=True)

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

    print(f"\nRunning OCR on: {image_path}\n")

    start = time.time()
    doc = DocumentFile.from_images(image_path)
    result = model(doc)
    elapsed = time.time() - start

    print(f"Processing time: {elapsed:.2f}s\n")

    # Render the text
    text = result.render()
    print("--- Extracted Text ---")
    print(text)

    print("\n" + "=" * 60)
    print("Test completed!")
    print("=" * 60)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        test_doctr(sys.argv[1])
    else:
        test_doctr()
