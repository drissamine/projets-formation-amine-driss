"""Test OCR on low-quality/blurry document photos."""

import sys
import cv2
import numpy as np
from pathlib import Path

BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR / "src"))

from ocr.low_quality_processor import LowQualityDocumentProcessor, BlurDetector
from ocr.engine import OCREngine
from ocr.extractor import FieldExtractor


def analyze_image(image_path: str):
    """Analyze image quality issues."""
    print(f"\n{'=' * 70}")
    print(f"ANALYZING IMAGE QUALITY")
    print(f"File: {image_path}")
    print("=" * 70)

    path = Path(image_path)
    if not path.exists():
        print(f"[ERROR] File not found")
        return None

    image = cv2.imread(str(path))
    if image is None:
        print(f"[ERROR] Cannot read image")
        return None

    # Convert to RGB
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Analyze quality
    processor = LowQualityDocumentProcessor()
    issues = processor.detect_quality_issues(image_rgb)

    print("\n[1] Quality Analysis:")
    print("-" * 50)

    print(f"  Resolution: {issues['resolution']}")
    if issues["low_resolution"]:
        print(f"    ⚠️  LOW RESOLUTION - Will upscale")

    print(f"  Blur Score: {issues['blur_score']:.2f}")
    if issues["is_blurry"]:
        print(f"    ⚠️  IMAGE IS BLURRY - Will deblur")

    print(f"  Brightness: {issues['mean_brightness']:.1f}")
    if issues["too_dark"]:
        print(f"    ⚠️  TOO DARK - Will brighten")
    elif issues["too_bright"]:
        print(f"    ⚠️  TOO BRIGHT - Will adjust")

    print(f"  Contrast: {issues['contrast']:.2f}")
    if issues["low_contrast"]:
        print(f"    ⚠️  LOW CONTRAST - Will enhance")

    print(f"  Noise Level: {issues['noise_level']:.2f}")
    if issues["noisy"]:
        print(f"    ⚠️  NOISY - Will denoise")

    # Detect blur type
    blur_type = BlurDetector.estimate_blur_type(image_rgb)
    print(f"  Blur Type: {blur_type}")

    return image_rgb, issues


def process_low_quality(image_path: str, save_debug: bool = True):
    """Process low-quality image with full pipeline."""
    result = analyze_image(image_path)
    if result is None:
        return

    image_rgb, issues = result
    path = Path(image_path)

    print(f"\n[2] Processing Image:")
    print("-" * 50)

    # Create output directory
    output_dir = BASE_DIR / "ocr_low_quality_results"
    output_dir.mkdir(exist_ok=True)

    # Save original
    if save_debug:
        orig_path = output_dir / f"{path.stem}_00_original.jpg"
        cv2.imwrite(str(orig_path), cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR))
        print(f"  Saved original: {orig_path}")

    # Initialize processor
    processor = LowQualityDocumentProcessor()

    # Check if aggressive processing needed
    needs_aggressive = any(
        [
            issues["is_blurry"],
            issues["low_contrast"],
            issues["noisy"],
            issues["low_resolution"],
        ]
    )

    print(f"\n  Using {'AGGRESSIVE' if needs_aggressive else 'STANDARD'} processing")

    # Process
    print("  Processing steps:")
    print("    - Auto-rotate...")
    print("    - Remove glare...")
    print("    - Enhance lighting...")
    if needs_aggressive:
        print("    - Deblur...")
    print("    - Upscale...")
    print("    - Denoise...")

    processed = processor.process(image_rgb, aggressive=needs_aggressive)

    # Save processed
    if save_debug:
        proc_path = output_dir / f"{path.stem}_01_processed.jpg"
        cv2.imwrite(str(proc_path), cv2.cvtColor(processed, cv2.COLOR_RGB2BGR))
        print(f"  Saved processed: {proc_path}")

    # Run OCR
    print(f"\n[3] Running OCR:")
    print("-" * 50)

    ocr = OCREngine()
    extractor = FieldExtractor()

    if not ocr.is_available():
        print("  [ERROR] No OCR engine available")
        return

    # Use EasyOCR (best for low quality)
    print("  Using EasyOCR...")
    text, conf = ocr._recognize_easyocr(processed)

    print(f"  OCR Confidence: {conf:.2f}")
    print(f"  Text Length: {len(text)} chars")

    # Show extracted text
    print(f"\n  --- EXTRACTED TEXT ---")
    print(text[:800] + "..." if len(text) > 800 else text)
    print("  --- END ---")

    # Extract fields
    print(f"\n[4] Extracting Fields:")
    print("-" * 50)

    doc_type, type_conf = extractor.detect_document_type(text)
    fields = extractor.extract_fields(text, doc_type)

    print(f"  Document Type: {doc_type} ({type_conf:.2f})")
    print(f"  Fields Found: {len(fields)}")

    if fields:
        print("\n  Extracted Fields:")
        for key, value in fields.items():
            print(f"    - {key}: {value}")
    else:
        print("  No fields extracted")

    # Summary
    print(f"\n{'=' * 70}")
    print("SUMMARY")
    print("=" * 70)
    print(f"Quality Issues Found:")
    if issues["is_blurry"]:
        print(f"  ✓ Blur corrected")
    if issues["low_resolution"]:
        print(f"  ✓ Resolution enhanced")
    if issues["low_contrast"]:
        print(f"  ✓ Contrast improved")
    if issues["noisy"]:
        print(f"  ✓ Noise reduced")

    print(f"\nResults:")
    print(f"  OCR Confidence: {conf:.2f}")
    print(f"  Characters: {len(text)}")
    print(f"  Fields: {len(fields)}")

    if save_debug:
        print(f"\nDebug images saved to: {output_dir}")

    return text, fields


def compare_processing(image_path: str):
    """Compare different processing methods."""
    print(f"\n{'=' * 70}")
    print(f"COMPARING PROCESSING METHODS")
    print(f"File: {image_path}")
    print("=" * 70)

    path = Path(image_path)
    image = cv2.imread(str(path))
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    output_dir = BASE_DIR / "ocr_low_quality_results"
    output_dir.mkdir(exist_ok=True)

    methods = [
        ("Original", lambda img: img),
        ("Quick Fix", LowQualityDocumentProcessor().quick_fix),
        ("Full Processing", LowQualityDocumentProcessor().process),
    ]

    ocr = OCREngine()
    best_result = None
    best_conf = 0

    for name, method in methods:
        print(f"\n{'-' * 70}")
        print(f"Method: {name}")
        print("-" * 70)

        try:
            # Process
            processed = method(image_rgb.copy())

            # Save
            out_path = output_dir / f"{path.stem}_{name.replace(' ', '_').lower()}.jpg"
            if len(processed.shape) == 2:
                cv2.imwrite(str(out_path), processed)
            else:
                cv2.imwrite(str(out_path), cv2.cvtColor(processed, cv2.COLOR_RGB2BGR))

            # OCR
            text, conf = ocr._recognize_easyocr(processed)

            print(f"Confidence: {conf:.2f}")
            print(f"Text: {text[:300]}...")

            if conf > best_conf:
                best_conf = conf
                best_result = (name, text, conf)

        except Exception as e:
            print(f"Error: {e}")

    print(f"\n{'=' * 70}")
    print("BEST METHOD")
    print("=" * 70)
    if best_result:
        print(f"Method: {best_result[0]}")
        print(f"Confidence: {best_result[2]:.2f}")
        print(f"Text: {best_result[1][:500]}...")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        image_path = sys.argv[1]

        # Check if user wants comparison mode
        if len(sys.argv) > 2 and sys.argv[2] == "--compare":
            compare_processing(image_path)
        else:
            process_low_quality(image_path)
    else:
        # Test with default images
        test_images = [
            BASE_DIR
            / "dataset"
            / "images"
            / "driver_license"
            / "permis-de-conduire-fr.png",
            BASE_DIR / "dataset" / "images" / "id_card" / "id_card_000.jpg",
        ]

        for img_path in test_images:
            if img_path.exists():
                process_low_quality(str(img_path))
                break
        else:
            print("Usage:")
            print(f"  python {sys.argv[0]} <image_path>")
            print(f"  python {sys.argv[0]} <image_path> --compare")
