"""Image preprocessing for better OCR results."""

import cv2
import numpy as np
from typing import Tuple, Optional


class DocumentPreprocessor:
    """Preprocess document images for optimal OCR."""

    def __init__(self, target_width: int = 1024):
        self.target_width = target_width

    def preprocess(self, image: np.ndarray) -> np.ndarray:
        """Apply full preprocessing pipeline."""
        # 1. Resize if too large/small
        image = self._resize(image)

        # 2. Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        else:
            gray = image

        # 3. Denoise
        denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)

        # 4. Deskew
        deskewed = self._deskew(denoised)

        # 5. Enhance contrast (CLAHE)
        enhanced = self._enhance_contrast(deskewed)

        # 6. Adaptive thresholding
        binary = self._adaptive_threshold(enhanced)

        # 7. Denoise again after thresholding
        final = cv2.medianBlur(binary, 3)

        return final

    def _resize(self, image: np.ndarray) -> np.ndarray:
        """Resize image maintaining aspect ratio."""
        height, width = image.shape[:2]
        if width > self.target_width * 1.5 or width < self.target_width * 0.5:
            scale = self.target_width / width
            new_width = int(width * scale)
            new_height = int(height * scale)
            return cv2.resize(
                image, (new_width, new_height), interpolation=cv2.INTER_LANCZOS4
            )
        return image

    def _deskew(self, image: np.ndarray) -> np.ndarray:
        """Correct image rotation."""
        # Detect edges
        edges = cv2.Canny(image, 50, 150, apertureSize=3)

        # Find lines using Hough transform
        lines = cv2.HoughLinesP(
            edges, 1, np.pi / 180, 100, minLineLength=100, maxLineGap=10
        )

        if lines is None or len(lines) == 0:
            return image

        # Calculate median angle
        angles = []
        for line in lines:
            x1, y1, x2, y2 = line[0]
            if x2 != x1:
                angle = np.degrees(np.arctan2(y2 - y1, x2 - x1))
                if -45 < angle < 45:  # Filter extreme angles
                    angles.append(angle)

        if not angles:
            return image

        median_angle = np.median(angles)

        # Rotate if significant skew detected
        if abs(median_angle) > 0.5:
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

        return image

    def _enhance_contrast(self, image: np.ndarray) -> np.ndarray:
        """Apply CLAHE for local contrast enhancement."""
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        return clahe.apply(image)

    def _adaptive_threshold(self, image: np.ndarray) -> np.ndarray:
        """Apply adaptive thresholding."""
        # Normalize
        normalized = cv2.normalize(image, None, 0, 255, cv2.NORM_MINMAX)

        # Adaptive threshold
        binary = cv2.adaptiveThreshold(
            normalized, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )
        return binary

    def crop_document(
        self, image: np.ndarray, bbox: Tuple[int, int, int, int], padding: int = 20
    ) -> np.ndarray:
        """Crop image to document bbox with padding."""
        x1, y1, x2, y2 = bbox

        # Add padding
        height, width = image.shape[:2]
        x1 = max(0, x1 - padding)
        y1 = max(0, y1 - padding)
        x2 = min(width, x2 + padding)
        y2 = min(height, y2 + padding)

        return image[y1:y2, x1:x2]

    def prepare_for_ocr(
        self, image: np.ndarray, bbox: Optional[Tuple] = None
    ) -> np.ndarray:
        """Full preparation pipeline with optional cropping."""
        if bbox is not None:
            image = self.crop_document(image, bbox)
        return self.preprocess(image)
