"""Test OCR on real photos with different preprocessing methods."""

import sys
import cv2
import numpy as np
from pathlib import Path

BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR / "src"))

from ocr.engine import OCREngine
from ocr.preprocessor_v2 import DocumentPreprocessorV2


def test_preprocessing_methods(image_path: str):
    """Test different preprocessing methods on a real photo."""
    print("=" * 70)
    print(f"Testing OCR on: {image_path}")
    print("=" * 70)

    path = Path(image_path)
    if not path.exists():
        print(f"[ERROR] File not found: {image_path}")
        return

    # Load image
    image = cv2.imread(str(path))
    if image is None:
        print(f"[ERROR] Cannot read image")
        return

    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    print(f"Original image: {image.shape}")

    # Initialize OCR
    ocr_engine = OCREngine()
    print(f"Available engines: {ocr_engine.get_available_engines()}")

    preprocessor = DocumentPreprocessorV2()

    # Test different methods
    methods = [
        (
            "Original (no preprocessing)",
            lambda img: (
                cv2.cvtColor(img, cv2.COLOR_RGB2GRAY) if len(img.shape) == 3 else img
            ),
        ),
        ("Tesseract optimized", preprocessor.preprocess_for_tesseract),
        ("Standard preprocessing", preprocessor.preprocess),
        ("Preserve color", preprocessor.preprocess_preserve_color),
    ]

    output_dir = path.parent / "ocr_test_results"
    output_dir.mkdir(exist_ok=True)

    best_result = None
    best_confidence = 0

    for method_name, method_func in methods:
        print(f"\n{'=' * 70}")
        print(f"Method: {method_name}")
        print("=" * 70)

        try:
            # Preprocess
            processed = method_func(image_rgb)

            # Save processed image
            output_path = (
                output_dir
                / f"{path.stem}_{method_name.replace(' ', '_').replace('(', '').replace(')', '')}.jpg"
            )
            cv2.imwrite(str(output_path), processed)
            print(f"Saved: {output_path}")

            # Run OCR
            text, conf = ocr_engine.recognize(processed)

            print(f"\nConfidence: {conf:.2f}")
            print(f"Text length: {len(text)} chars")
            print(f"\n--- EXTRACTED TEXT ---")
            print(text[:800] + "..." if len(text) > 800 else text)
            print("--- END ---")

            if conf > best_confidence:
                best_confidence = conf
                best_result = (method_name, text, conf)

        except Exception as e:
            print(f"[ERROR] {e}")

    print(f"\n{'=' * 70}")
    print("SUMMARY")
    print("=" * 70)
    if best_result:
        print(f"Best method: {best_result[0]}")
        print(f"Confidence: {best_result[2]:.2f}")
    else:
        print("No successful OCR results")

    print(f"\nProcessed images saved to: {output_dir}")


def main():
    # Check for command line argument
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
    else:
        # Default test images
        test_images = [
            "dataset/images/driver_license/permis-de-conduire-fr.png",
            "dataset/images/id_card/id_card_000.jpg",
            "dataset/images/passport/passport_001.jpg",
        ]

        for img_path in test_images:
            full_path = BASE_DIR / img_path
            if full_path.exists():
                test_preprocessing_methods(str(full_path))
                break
        else:
            print("No test images found")
            print("Usage: python test_ocr_real.py <image_path>")


if __name__ == "__main__":
    main()
