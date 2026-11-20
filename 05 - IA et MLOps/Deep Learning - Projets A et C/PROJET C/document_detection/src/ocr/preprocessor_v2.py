"""Improved image preprocessing for real document photos."""

import cv2
import numpy as np
from typing import Tuple, Optional


class DocumentPreprocessorV2:
    """Advanced preprocessing for real document photos."""

    def __init__(self, target_width: int = 1024):
        self.target_width = target_width

    def preprocess(self, image: np.ndarray) -> np.ndarray:
        """Apply full preprocessing pipeline optimized for documents."""
        # Keep original for reference
        original = image.copy()

        # 1. Resize if needed
        image = self._smart_resize(image)

        # 2. Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        else:
            gray = image

        # 3. Light denoising (preserve text)
        denoised = cv2.fastNlMeansDenoising(gray, None, 5, 7, 21)

        # 4. Mild Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(denoised, (3, 3), 0)

        # 5. CLAHE for contrast (milder settings)
        clahe = cv2.createCLAHE(clipLimit=1.5, tileGridSize=(8, 8))
        enhanced = clahe.apply(blurred)

        # 6. Simple thresholding (better for text than adaptive sometimes)
        _, binary = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        return binary

    def preprocess_preserve_color(self, image: np.ndarray) -> np.ndarray:
        """Preprocessing that preserves more detail."""
        # Resize
        image = self._smart_resize(image)

        # Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        else:
            gray = image

        # Normalize lighting
        normalized = cv2.normalize(gray, None, 0, 255, cv2.NORM_MINMAX)

        # CLAHE
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(normalized)

        return enhanced

    def preprocess_for_tesseract(self, image: np.ndarray) -> np.ndarray:
        """Optimized preprocessing specifically for Tesseract."""
        # Resize maintaining aspect ratio
        image = self._smart_resize(image)

        # Grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        else:
            gray = image

        # Deskew if needed
        deskewed = self._deskew(gray)

        # Scale up if image is small (Tesseract likes 300 DPI)
        height, width = deskewed.shape
        if width < 1000:
            scale = 1000 / width
            new_width = int(width * scale)
            new_height = int(height * scale)
            deskewed = cv2.resize(
                deskewed, (new_width, new_height), interpolation=cv2.INTER_CUBIC
            )

        # Otsu threshold
        _, binary = cv2.threshold(deskewed, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # Dilate slightly to connect broken text
        kernel = np.ones((1, 1), np.uint8)
        dilated = cv2.dilate(binary, kernel, iterations=1)

        return dilated

    def _smart_resize(self, image: np.ndarray) -> np.ndarray:
        """Resize maintaining aspect ratio, but not too small."""
        height, width = image.shape[:2]

        # Don't upscale too much, don't downscale too much
        if width > 2000:
            scale = 1500 / width
            new_width = int(width * scale)
            new_height = int(height * scale)
            return cv2.resize(
                image, (new_width, new_height), interpolation=cv2.INTER_AREA
            )

        return image

    def _deskew(self, image: np.ndarray) -> np.ndarray:
        """Correct rotation if significant."""
        # Detect edges
        edges = cv2.Canny(image, 50, 150)

        # Find lines
        lines = cv2.HoughLinesP(
            edges, 1, np.pi / 180, 100, minLineLength=100, maxLineGap=10
        )

        if lines is None:
            return image

        angles = []
        for line in lines:
            x1, y1, x2, y2 = line[0]
            if x2 != x1:
                angle = np.degrees(np.arctan2(y2 - y1, x2 - x1))
                if abs(angle) < 30:  # Reasonable angles only
                    angles.append(angle)

        if not angles:
            return image

        median_angle = np.median(angles)

        if abs(median_angle) < 1.0:  # Don't rotate for small angles
            return image

        # Rotate
        height, width = image.shape[:2]
        center = (width // 2, height // 2)
        rotation_matrix = cv2.getRotationMatrix2D(center, median_angle, 1.0)
        rotated = cv2.warpAffine(
            image,
            rotation_matrix,
            (width, height),
            borderMode=cv2.BORDER_CONSTANT,
            borderValue=255,
        )
        return rotated

    def crop_document(
        self, image: np.ndarray, bbox: Tuple[int, int, int, int], padding: int = 20
    ) -> np.ndarray:
        """Crop to document region with padding."""
        x1, y1, x2, y2 = bbox

        height, width = image.shape[:2]
        x1 = max(0, x1 - padding)
        y1 = max(0, y1 - padding)
        x2 = min(width, x2 + padding)
        y2 = min(height, y2 + padding)

        return image[y1:y2, x1:x2]

    def remove_glare(self, image: np.ndarray) -> np.ndarray:
        """Remove glare/bright spots."""
        if len(image.shape) == 3:
            lab = cv2.cvtColor(image, cv2.COLOR_RGB2LAB)
            l, a, b = cv2.split(lab)

            # Inpaint bright areas
            _, bright_mask = cv2.threshold(l, 240, 255, cv2.THRESH_BINARY)
            l_inpainted = cv2.inpaint(l, bright_mask, 3, cv2.INPAINT_TELEA)

            lab = cv2.merge([l_inpainted, a, b])
            result = cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)
            return result

        return image

    def auto_rotate(self, image: np.ndarray, text: str = None) -> np.ndarray:
        """Auto-rotate based on text orientation."""
        # Try different rotations and pick best
        rotations = [0, 90, 180, 270]
        best_image = image
        best_score = 0

        for angle in rotations:
            rotated = self._rotate_image(image, angle)
            # Score based on text alignment (would need OCR here)
            # For now, just return original
            pass

        return best_image

    def _rotate_image(self, image: np.ndarray, angle: int) -> np.ndarray:
        """Rotate image by angle."""
        if angle == 0:
            return image

        height, width = image.shape[:2]
        center = (width // 2, height // 2)

        rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(
            image,
            rotation_matrix,
            (width, height),
            borderMode=cv2.BORDER_CONSTANT,
            borderValue=255,
        )
        return rotated
