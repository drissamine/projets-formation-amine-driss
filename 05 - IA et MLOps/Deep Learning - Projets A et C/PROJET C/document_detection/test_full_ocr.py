"""Full OCR test - Detection + EasyOCR extraction."""

import sys
import cv2
from pathlib import Path
from ultralytics import YOLO

BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR / "src"))

from ocr.engine import OCREngine
from ocr.extractor import FieldExtractor


def test_full_pipeline(image_path: str):
    """Test complete OCR pipeline: detection + OCR + field extraction."""
    print(f"\n{'=' * 70}")
    print(f"FULL OCR PIPELINE TEST")
    print(f"File: {image_path}")
    print("=" * 70)

    path = Path(image_path)
    if not path.exists():
        print(f"[ERROR] File not found")
        return

    # Step 1: Document Detection
    print("\n[1] Loading YOLO model...")
    try:
        model = YOLO(str(BASE_DIR / "models" / "document_detector.pt"))
        print("    Model loaded successfully")
    except Exception as e:
        print(f"    [WARNING] Could not load custom model: {e}")
        print("    Falling back to yolov8n...")
        model = YOLO("yolov8n.pt")

    # Load image
    image = cv2.imread(str(path))
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    print("\n[2] Running document detection...")
    results = model(image_rgb, verbose=False)

    if len(results[0].boxes) == 0:
        print("    [WARNING] No document detected, using full image")
        detected_region = image_rgb
        doc_class = "unknown"
        conf = 0
    else:
        # Get best detection
        box = results[0].boxes[0]
        x1, y1, x2, y2 = [int(c) for c in box.xyxy[0]]
        conf = float(box.conf[0])
        cls = int(box.cls[0])

        DOC_CLASSES = {
            0: "id_card",
            1: "driver_license",
            2: "residence_permit",
            3: "passport",
        }
        doc_class = DOC_CLASSES.get(cls, "unknown")

        print(f"    Detected: {doc_class} (conf: {conf:.2f})")
        print(f"    Bbox: [{x1}, {y1}, {x2}, {y2}]")

        # Crop document
        h, w = image_rgb.shape[:2]
        x1 = max(0, x1 - 20)
        y1 = max(0, y1 - 20)
        x2 = min(w, x2 + 20)
        y2 = min(h, y2 + 20)
        detected_region = image_rgb[y1:y2, x1:x2]

    # Step 2: OCR
    print("\n[3] Running OCR with EasyOCR...")
    ocr = OCREngine()

    if not ocr.is_available():
        print("    [ERROR] No OCR engine available")
        return

    # Use EasyOCR (works better for photos)
    text, ocr_conf = ocr._recognize_easyocr(detected_region)

    print(f"    OCR confidence: {ocr_conf:.2f}")
    print(f"    Text length: {len(text)} chars")
    print(f"\n--- EXTRACTED TEXT ---")
    print(text[:600] + "..." if len(text) > 600 else text)
    print("--- END TEXT ---")

    # Step 3: Field Extraction
    print("\n[4] Extracting fields...")
    extractor = FieldExtractor()

    # Detect document type from text
    detected_type, type_conf = extractor.detect_document_type(text)
    print(f"    Detected type from text: {detected_type} (conf: {type_conf:.2f})")

    # Use YOLO detection if confident
    if conf > 0.5:
        detected_type = doc_class
        print(f"    Using YOLO type: {doc_class}")

    # Extract fields
    fields = extractor.extract_fields(text, detected_type)

    print(f"\n    EXTRACTED FIELDS:")
    print(f"    {'-' * 40}")
    for key, value in fields.items():
        print(f"    {key:20s}: {value}")
    print(f"    {'-' * 40}")

    # Summary
    print(f"\n{'=' * 70}")
    print("SUMMARY")
    print("=" * 70)
    print(f"Document type: {detected_type}")
    print(f"Detection confidence: {conf:.2f}")
    print(f"OCR confidence: {ocr_conf:.2f}")
    print(f"Fields extracted: {len(fields)}")
    print(f"\nKey fields:")
    if "nom" in fields:
        print(f"  - Nom: {fields['nom']}")
    if "prenom" in fields:
        print(f"  - Prénom: {fields['prenom']}")
    if "date_naissance" in fields:
        print(f"  - Date de naissance: {fields['date_naissance']}")
    print("=" * 70)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        test_full_pipeline(sys.argv[1])
    else:
        # Test with available images
        test_images = [
            BASE_DIR
            / "dataset"
            / "images"
            / "driver_license"
            / "permis-de-conduire-fr.png",
            BASE_DIR / "dataset" / "images" / "id_card" / "id_card_000.jpg",
            BASE_DIR / "dataset" / "images" / "passport" / "passport_001.jpg",
        ]

        for img_path in test_images:
            if img_path.exists():
                test_full_pipeline(str(img_path))
                break
        else:
            print("No test images found")
            print(f"Usage: python {__file__} <image_path>")
