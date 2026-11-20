"""Advanced preprocessing for low-quality document photos.

Handles:
- Blurry images (out of focus or motion blur)
- Noisy images (high ISO, compression artifacts)
- Uneven lighting (shadows, glare)
- Low resolution (small text)
- Skewed/rotated photos
"""

import cv2
import numpy as np
from typing import Tuple, Optional
from scipy import ndimage
from PIL import Image, ImageEnhance, ImageFilter


class LowQualityDocumentProcessor:
    """Process low-quality document photos for OCR."""

    def __init__(self):
        self.min_text_height = 30  # Minimum text height in pixels

    def process(self, image: np.ndarray, aggressive: bool = True) -> np.ndarray:
        """
        Full processing pipeline for low-quality images.

        Args:
            image: Input image (BGR or RGB)
            aggressive: Use aggressive processing for very poor quality

        Returns:
            Processed image optimized for OCR
        """
        # Convert to RGB if needed
        if len(image.shape) == 3 and image.shape[2] == 3:
            if self._is_bgr(image):
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Step 1: Auto-rotate if needed
        image = self._auto_rotate(image)

        # Step 2: Remove glare/shine
        image = self._remove_glare(image)

        # Step 3: Enhance lighting
        image = self._enhance_lighting(image)

        # Step 4: Deblur if needed
        if aggressive:
            image = self._deblur(image)

        # Step 5: Upscale for OCR
        image = self._upscale_for_ocr(image)

        # Step 6: Enhance sharpness
        image = self._enhance_sharpness(image)

        # Step 7: Denoise
        image = self._smart_denoise(image)

        # Step 8: Final contrast enhancement
        image = self._final_enhancement(image)

        return image

    def _is_bgr(self, image: np.ndarray) -> bool:
        """Check if image is in BGR format."""
        # Simple heuristic: check if blue channel is higher than red
        # in areas that should be white/light
        return False  # Assume RGB for now

    def _auto_rotate(self, image: np.ndarray) -> np.ndarray:
        """Detect and correct rotation."""
        gray = (
            cv2.cvtColor(image, cv2.COLOR_RGB2GRAY) if len(image.shape) == 3 else image
        )

        # Detect edges
        edges = cv2.Canny(gray, 50, 150)

        # Find lines
        lines = cv2.HoughLinesP(
            edges, 1, np.pi / 180, 100, minLineLength=100, maxLineGap=10
        )

        if lines is None or len(lines) < 5:
            return image

        # Calculate angles
        angles = []
        for line in lines:
            x1, y1, x2, y2 = line[0]
            if x2 != x1:
                angle = np.degrees(np.arctan2(y2 - y1, x2 - x1))
                if abs(angle) < 45:  # Reasonable angles only
                    angles.append(angle)

        if not angles:
            return image

        # Get median angle
        median_angle = np.median(angles)

        if abs(median_angle) < 1.0:
            return image

        # Rotate
        height, width = image.shape[:2]
        center = (width // 2, height // 2)
        rotation_matrix = cv2.getRotationMatrix2D(center, median_angle, 1.0)

        # Calculate new size
        abs_cos = abs(rotation_matrix[0, 0])
        abs_sin = abs(rotation_matrix[0, 1])
        new_width = int(height * abs_sin + width * abs_cos)
        new_height = int(height * abs_cos + width * abs_sin)

        # Adjust rotation matrix
        rotation_matrix[0, 2] += (new_width - width) / 2
        rotation_matrix[1, 2] += (new_height - height) / 2

        rotated = cv2.warpAffine(
            image,
            rotation_matrix,
            (new_width, new_height),
            borderMode=cv2.BORDER_CONSTANT,
            borderValue=(255, 255, 255),
        )

        return rotated

    def _remove_glare(self, image: np.ndarray) -> np.ndarray:
        """Remove bright glare spots."""
        # Convert to LAB color space
        lab = cv2.cvtColor(image, cv2.COLOR_RGB2LAB)
        l, a, b = cv2.split(lab)

        # Detect very bright areas (glare)
        _, bright_mask = cv2.threshold(l, 240, 255, cv2.THRESH_BINARY)

        if np.sum(bright_mask) > 0:
            # Dilate mask slightly
            kernel = np.ones((5, 5), np.uint8)
            bright_mask = cv2.dilate(bright_mask, kernel, iterations=1)

            # Inpaint bright areas
            l_inpainted = cv2.inpaint(l, bright_mask, 3, cv2.INPAINT_TELEA)

            # Merge back
            lab = cv2.merge([l_inpainted, a, b])
            image = cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)

        return image

    def _enhance_lighting(self, image: np.ndarray) -> np.ndarray:
        """Correct uneven lighting."""
        # Convert to LAB
        lab = cv2.cvtColor(image, cv2.COLOR_RGB2LAB)
        l, a, b = cv2.split(lab)

        # Apply CLAHE to L channel
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        l_enhanced = clahe.apply(l)

        # Merge back
        lab = cv2.merge([l_enhanced, a, b])
        image = cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)

        return image

    def _deblur(self, image: np.ndarray) -> np.ndarray:
        """Reduce blur using deconvolution."""
        # Estimate blur
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()

        if laplacian_var > 100:  # Not too blurry
            return image

        # Convert PIL for easier processing
        pil_img = Image.fromarray(image)

        # Sharpen
        enhancer = ImageEnhance.Sharpness(pil_img)
        pil_img = enhancer.enhance(2.0)

        return np.array(pil_img)

    def _upscale_for_ocr(self, image: np.ndarray) -> np.ndarray:
        """Upscale to optimal size for OCR."""
        height, width = image.shape[:2]

        # Target: at least 2000px width for good OCR
        if width < 1500:
            scale = 2000 / width
            new_width = int(width * scale)
            new_height = int(height * scale)

            # Use Lanczos interpolation (best for upscaling)
            image = cv2.resize(
                image, (new_width, new_height), interpolation=cv2.INTER_LANCZOS4
            )

        return image

    def _enhance_sharpness(self, image: np.ndarray) -> np.ndarray:
        """Enhance edge sharpness."""
        # Unsharp mask
        gaussian = cv2.GaussianBlur(image, (0, 0), 3)
        image = cv2.addWeighted(image, 1.5, gaussian, -0.5, 0)

        return image

    def _smart_denoise(self, image: np.ndarray) -> np.ndarray:
        """Remove noise while preserving edges."""
        # Convert to grayscale for denoising
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            # Denoise grayscale
            denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
            return cv2.cvtColor(denoised, cv2.COLOR_GRAY2RGB)
        else:
            return cv2.fastNlMeansDenoising(image, None, 10, 7, 21)

    def _final_enhancement(self, image: np.ndarray) -> np.ndarray:
        """Final contrast enhancement."""
        pil_img = Image.fromarray(image)

        # Enhance contrast
        enhancer = ImageEnhance.Contrast(pil_img)
        pil_img = enhancer.enhance(1.2)

        # Enhance sharpness slightly
        enhancer = ImageEnhance.Sharpness(pil_img)
        pil_img = enhancer.enhance(1.1)

        return np.array(pil_img)

    def detect_quality_issues(self, image: np.ndarray) -> dict:
        """Analyze image and report quality issues."""
        gray = (
            cv2.cvtColor(image, cv2.COLOR_RGB2GRAY) if len(image.shape) == 3 else image
        )

        issues = {}

        # Check blur
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        issues["blur_score"] = laplacian_var
        issues["is_blurry"] = laplacian_var < 100

        # Check brightness
        mean_brightness = np.mean(gray)
        issues["mean_brightness"] = mean_brightness
        issues["too_dark"] = mean_brightness < 50
        issues["too_bright"] = mean_brightness > 200

        # Check contrast
        std_brightness = np.std(gray)
        issues["contrast"] = std_brightness
        issues["low_contrast"] = std_brightness < 30

        # Check noise
        noise_score = self._estimate_noise(gray)
        issues["noise_level"] = noise_score
        issues["noisy"] = noise_score > 10

        # Check resolution
        height, width = image.shape[:2]
        issues["resolution"] = f"{width}x{height}"
        issues["low_resolution"] = width < 1000

        return issues

    def _estimate_noise(self, gray: np.ndarray) -> float:
        """Estimate noise level in image."""
        # Use median absolute deviation
        median = np.median(gray)
        mad = np.median(np.abs(gray - median))
        return mad

    def quick_fix(self, image: np.ndarray) -> np.ndarray:
        """Quick fix for moderately poor quality images."""
        # Just the essentials
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        else:
            gray = image

        # Upscale
        h, w = gray.shape
        if w < 1500:
            scale = 2000 / w
            gray = cv2.resize(
                gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC
            )

        # CLAHE
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)

        # Mild denoise
        denoised = cv2.fastNlMeansDenoising(enhanced, None, 5, 7, 21)

        # Sharpen
        kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
        sharpened = cv2.filter2D(denoised, -1, kernel)

        return sharpened


class BlurDetector:
    """Detect and measure image blur."""

    @staticmethod
    def detect_blur(image: np.ndarray, threshold: float = 100.0) -> Tuple[bool, float]:
        """
        Detect if image is blurry.

        Returns:
            Tuple of (is_blurry, blur_score)
        """
        gray = (
            cv2.cvtColor(image, cv2.COLOR_RGB2GRAY) if len(image.shape) == 3 else image
        )

        # Compute Laplacian variance
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()

        is_blurry = laplacian_var < threshold

        return is_blurry, laplacian_var

    @staticmethod
    def estimate_blur_type(image: np.ndarray) -> str:
        """
        Estimate type of blur.

        Returns:
            'motion', 'focus', 'none'
        """
        gray = (
            cv2.cvtColor(image, cv2.COLOR_RGB2GRAY) if len(image.shape) == 3 else image
        )

        # Calculate gradients in x and y directions
        sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)

        # Directional variance
        x_var = np.var(sobelx)
        y_var = np.var(sobely)

        ratio = x_var / (y_var + 1e-10)

        if ratio > 2 or ratio < 0.5:
            return "motion"
        elif np.var(cv2.Laplacian(gray, cv2.CV_64F)) < 100:
            return "focus"
        else:
            return "none"
