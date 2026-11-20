"""Test script for improved OCR functionality."""

import sys
from pathlib import Path

# Add src to path
BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR / "src"))

import cv2
import numpy as np
from ocr import DocumentPreprocessor, OCREngine, FieldExtractor


def test_preprocessor():
    """Test image preprocessing."""
    print("=" * 60)
    print("Testing Document Preprocessor")
    print("=" * 60)

    preprocessor = DocumentPreprocessor(target_width=1024)

    # Test with a sample image if available
    sample_paths = [
        BASE_DIR / "dataset" / "images" / "id_card" / "id_card_000.jpg",
        BASE_DIR / "dataset" / "images" / "passport" / "passport_000.jpg",
    ]

    for path in sample_paths:
        if path.exists():
            print(f"\nProcessing: {path.name}")
            image = cv2.imread(str(path))
            if image is not None:
                image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                processed = preprocessor.preprocess(image_rgb)
                print(f"  Original shape: {image.shape}")
                print(f"  Processed shape: {processed.shape}")
                print(f"  [OK] Preprocessing successful")
            break
    else:
        print("  No sample images found")


def test_ocr_engine():
    """Test OCR engine."""
    print("\n" + "=" * 60)
    print("Testing OCR Engine")
    print("=" * 60)

    engine = OCREngine(preferred_engine="auto")

    print(f"\nTesseract available: {engine.tesseract_available}")
    print(f"EasyOCR available: {engine.easyocr_available}")
    print(f"Available engines: {engine.get_available_engines()}")

    if engine.is_available():
        # Test with a simple image
        test_image = np.ones((200, 400), dtype=np.uint8) * 255
        cv2.putText(test_image, "Test", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 2, 0, 3)

        text, conf = engine.recognize(test_image)
        print(f"\n[OK] OCR test completed")
        print(f"  Text: '{text[:50]}...'" if len(text) > 50 else f"  Text: '{text}'")
        print(f"  Confidence: {conf:.2f}")
    else:
        print("\n[ERROR] No OCR engine available")
        print("  Install Tesseract: https://github.com/UB-Mannheim/tesseract/wiki")
        print("  Or install EasyOCR: pip install easyocr")


def test_field_extractor():
    """Test field extraction."""
    print("\n" + "=" * 60)
    print("Testing Field Extractor")
    print("=" * 60)

    extractor = FieldExtractor()

    # Sample texts for testing
    test_cases = [
        (
            "Carte d'identité nationale\nNom: DUPONT\nPrénom: Jean\nNé le: 15/03/1990",
            "id_card",
        ),
        ("Permis de conduire\nDélivré le: 01/01/2020", "driver_license"),
        ("Unknown document\nSome random text", "unknown"),
    ]

    for text, expected_type in test_cases:
        doc_type, conf = extractor.detect_document_type(text)
        fields = extractor.extract_fields(text, doc_type)

        print(f"\nInput: {text[:50]}...")
        print(f"  Detected type: {doc_type} (confidence: {conf:.2f})")
        print(f"  Expected: {expected_type}")
        print(f"  Fields: {fields}")


def test_full_pipeline():
    """Test full OCR pipeline."""
    print("\n" + "=" * 60)
    print("Testing Full OCR Pipeline")
    print("=" * 60)

    preprocessor = DocumentPreprocessor()
    ocr_engine = OCREngine()
    extractor = FieldExtractor()

    # Find a test image
    test_images = [
        BASE_DIR / "dataset" / "images" / "id_card" / "id_card_000.jpg",
        BASE_DIR / "dataset" / "images" / "passport" / "passport_000.jpg",
    ]

    for img_path in test_images:
        if not img_path.exists():
            continue

        print(f"\nProcessing: {img_path}")

        # Load image
        image = cv2.imread(str(img_path))
        if image is None:
            continue

        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Preprocess
        print("  1. Preprocessing...")
        processed = preprocessor.preprocess(image_rgb)

        # OCR
        print("  2. Running OCR...")
        if ocr_engine.is_available():
            text, conf = ocr_engine.recognize(processed)
            print(f"     Text length: {len(text)} chars")
            print(f"     Confidence: {conf:.2f}")

            # Extract fields
            print("  3. Extracting fields...")
            doc_type, type_conf = extractor.detect_document_type(text)
            fields = extractor.extract_fields(text, doc_type)

            print(f"     Document type: {doc_type}")
            print(f"     Fields: {fields}")
        else:
            print("     ✗ No OCR engine available")

            print(" [OK] Pipeline completed")
        break


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("Document OCR - Test Suite")
    print("=" * 60)

    test_preprocessor()
    test_ocr_engine()
    test_field_extractor()
    test_full_pipeline()

    print("\n" + "=" * 60)
    print("Tests completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
