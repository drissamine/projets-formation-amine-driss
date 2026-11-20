"""Test OCR on a specific file."""

import sys
from pathlib import Path

BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR / "src"))

import cv2
from ocr import DocumentPreprocessor, OCREngine, FieldExtractor


def test_file(file_path: str):
    """Test OCR on a single file."""
    print("=" * 60)
    print(f"Testing file: {file_path}")
    print("=" * 60)

    path = Path(file_path)
    if not path.exists():
        print(f"[ERROR] File not found: {file_path}")
        return

    # Initialize components
    preprocessor = DocumentPreprocessor(target_width=1024)
    ocr_engine = OCREngine()
    extractor = FieldExtractor()

    print(f"\nEngines available: {ocr_engine.get_available_engines()}")

    # Load image
    print(f"\n[1] Loading image...")
    image = cv2.imread(str(path))
    if image is None:
        print(f"[ERROR] Cannot read image: {file_path}")
        return

    print(f"    Image shape: {image.shape}")
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Preprocess
    print(f"\n[2] Preprocessing...")
    processed = preprocessor.preprocess(image_rgb)
    print(f"    Processed shape: {processed.shape}")

    # Save preprocessed for inspection
    output_path = path.parent / f"{path.stem}_preprocessed.jpg"
    cv2.imwrite(str(output_path), processed)
    print(f"    Saved preprocessed: {output_path}")

    # OCR
    print(f"\n[3] Running OCR...")
    if ocr_engine.is_available():
        text, conf = ocr_engine.recognize(processed)
        print(f"    OCR Confidence: {conf:.2f}")
        print(f"    Text length: {len(text)} chars")
        print(f"\n--- RAW TEXT ---")
        print(text[:500] + "..." if len(text) > 500 else text)
        print("--- END TEXT ---")

        # Extract fields
        print(f"\n[4] Extracting fields...")
        doc_type, type_conf = extractor.detect_document_type(text)
        fields = extractor.extract_fields(text, doc_type)

        print(f"    Document type: {doc_type} (confidence: {type_conf:.2f})")
        print(f"\n    Extracted fields:")
        for key, value in fields.items():
            print(f"      - {key}: {value}")
    else:
        print("    [ERROR] No OCR engine available")

    print("\n" + "=" * 60)
    print("Test completed!")
    print("=" * 60)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        test_file(sys.argv[1])
    else:
        # Test default file
        test_file("dataset/images/driver_license/permis-de-conduire-fr.png")
