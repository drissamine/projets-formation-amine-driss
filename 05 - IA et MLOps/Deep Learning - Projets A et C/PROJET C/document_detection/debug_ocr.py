"""Debug OCR issues - analyze why text becomes garbled."""

import cv2
import numpy as np
from pathlib import Path
import sys

# Check if image file provided
if len(sys.argv) < 2:
    print("Usage: python debug_ocr.py <image_path>")
    print("\nThis script will:")
    print("1. Show the original image info")
    print("2. Save multiple preprocessing variations")
    print("3. Test OCR on each variation")
    print("4. Identify the best approach")
    sys.exit(1)

image_path = sys.argv[1]
path = Path(image_path)

if not path.exists():
    print(f"Error: File not found: {image_path}")
    sys.exit(1)

print(f"\n{'=' * 70}")
print(f"OCR DEBUG - Analyzing: {path.name}")
print("=" * 70)

# Load image
image = cv2.imread(str(path))
if image is None:
    print(f"Error: Cannot read image")
    sys.exit(1)

print(f"\nImage properties:")
print(f"  Dimensions: {image.shape[1]} x {image.shape[0]} pixels")
print(f"  Channels: {image.shape[2] if len(image.shape) > 2 else 1}")

# Convert to RGB for display
if len(image.shape) == 3:
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
else:
    image_rgb = image
    gray = image

# Output directory
output_dir = Path("ocr_debug_analysis")
output_dir.mkdir(exist_ok=True)

# Save original
original_path = output_dir / f"{path.stem}_00_original.jpg"
cv2.imwrite(str(original_path), image)
print(f"  Saved original to: {original_path}")

# Define preprocessing strategies
strategies = []


# Strategy 1: Just grayscale (no processing)
def method_just_gray(img):
    return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img


strategies.append(("01_just_grayscale", method_just_gray))


# Strategy 2: Resize only (upscale small images)
def method_resize_only(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img
    h, w = gray.shape
    if w < 1000:
        scale = 1500 / w
        resized = cv2.resize(
            gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC
        )
        return resized
    return gray


strategies.append(("02_resize_only", method_resize_only))


# Strategy 3: Resize + Otsu
def method_resize_otsu(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img
    h, w = gray.shape
    if w < 1000:
        scale = 1500 / w
        gray = cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return binary


strategies.append(("03_resize_otsu", method_resize_otsu))


# Strategy 4: Denoise + Resize + Otsu
def method_denoise_resize_otsu(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img
    denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
    h, w = denoised.shape
    if w < 1000:
        scale = 1500 / w
        denoised = cv2.resize(
            denoised, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC
        )
    _, binary = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return binary


strategies.append(("04_denoise_resize_otsu", method_denoise_resize_otsu))


# Strategy 5: CLAHE + Resize
def method_clahe_resize(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)
    h, w = enhanced.shape
    if w < 1000:
        scale = 1500 / w
        enhanced = cv2.resize(
            enhanced, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC
        )
    return enhanced


strategies.append(("05_clahe_resize", method_clahe_resize))


# Strategy 6: Resize + Adaptive threshold
def method_resize_adaptive(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img
    h, w = gray.shape
    if w < 1000:
        scale = 1500 / w
        gray = cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
    binary = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
    )
    return binary


strategies.append(("06_resize_adaptive", method_resize_adaptive))

# Apply each strategy and save
print(f"\n{'=' * 70}")
print("Applying preprocessing strategies...")
print("=" * 70)

for name, func in strategies:
    try:
        processed = func(image)
        output_path = output_dir / f"{path.stem}_{name}.jpg"
        cv2.imwrite(str(output_path), processed)
        print(f"  ✓ {name}: {processed.shape}")
    except Exception as e:
        print(f"  ✗ {name}: {e}")

print(f"\n{'=' * 70}")
print("Preprocessing complete!")
print("=" * 70)
print(f"\nFiles saved to: {output_dir}")
print("\nNow test OCR on these files to see which preprocessing works best.")
print(f"\nSuggested test:")
print(
    f"  python test_easyocr_only.py {output_dir / (path.stem + '_02_resize_only.jpg')}"
)
