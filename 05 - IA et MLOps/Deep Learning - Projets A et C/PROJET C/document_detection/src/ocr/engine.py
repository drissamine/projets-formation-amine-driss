"""OCR Engine supporting multiple backends."""

import os
import re
import cv2
import numpy as np
from PIL import Image
from typing import Optional, List, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OCREngine:
    """OCR Engine with support for Tesseract and EasyOCR."""

    def __init__(self, preferred_engine: str = "auto"):
        self.preferred_engine = preferred_engine
        self.tesseract_available = False
        self.easyocr_available = False
        self.easyocr_reader = None
        self.tesseract_cmd = None

        self._init_tesseract()
        self._init_easyocr()

    def _init_tesseract(self):
        """Initialize Tesseract OCR."""
        tesseract_paths = [
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
            os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\WinGet\Packages\Tesseract"),
        ]

        for path in tesseract_paths:
            if os.path.isfile(path):
                self.tesseract_cmd = path
                self.tesseract_available = True
                logger.info(f"Tesseract found: {path}")
                break
            elif os.path.isdir(path):
                for root, dirs, files in os.walk(path):
                    if "tesseract.exe" in files:
                        self.tesseract_cmd = os.path.join(root, "tesseract.exe")
                        self.tesseract_available = True
                        logger.info(f"Tesseract found: {self.tesseract_cmd}")
                        break

        if self.tesseract_available:
            try:
                import pytesseract

                pytesseract.pytesseract.tesseract_cmd = self.tesseract_cmd
            except ImportError:
                logger.warning("pytesseract not installed")
                self.tesseract_available = False

    def _init_easyocr(self):
        """Initialize EasyOCR."""
        try:
            import easyocr

            self.easyocr_reader = easyocr.Reader(["fr", "en"], gpu=False)
            self.easyocr_available = True
            logger.info("EasyOCR initialized")
        except ImportError:
            logger.warning("easyocr not installed")
        except Exception as e:
            logger.warning(f"EasyOCR initialization failed: {e}")

    def recognize(self, image: np.ndarray, engine: str = "auto") -> Tuple[str, float]:
        """
        Perform OCR on image.

        Returns:
            Tuple of (text, confidence)
        """
        if engine == "auto":
            if self.easyocr_available:
                engine = "easyocr"
            elif self.tesseract_available:
                engine = "tesseract"
            else:
                return "", 0.0

        if engine == "easyocr" and self.easyocr_available:
            return self._recognize_easyocr(image)
        elif engine == "tesseract" and self.tesseract_available:
            return self._recognize_tesseract(image)
        else:
            return "", 0.0

    def _recognize_easyocr(self, image: np.ndarray) -> Tuple[str, float]:
        """Use EasyOCR for recognition."""
        try:
            # Convert to RGB if needed
            if len(image.shape) == 2:  # Grayscale
                image_rgb = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
            elif image.shape[2] == 3:  # Already RGB or BGR
                image_rgb = image
            else:
                image_rgb = cv2.cvtColor(image, cv2.COLOR_RGBA2RGB)

            results = self.easyocr_reader.readtext(image_rgb)

            if not results:
                return "", 0.0

            # Concatenate all text
            texts = []
            confidences = []
            for bbox, text, conf in results:
                if text.strip():
                    texts.append(text)
                    confidences.append(conf)

            full_text = "\n".join(texts)
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0

            return full_text, avg_confidence

        except Exception as e:
            logger.error(f"EasyOCR error: {e}")
            return "", 0.0

    def _recognize_tesseract(self, image: np.ndarray) -> Tuple[str, float]:
        """Use Tesseract for recognition."""
        try:
            import pytesseract

            pil_image = Image.fromarray(image)

            # Get detailed data including confidence
            data = pytesseract.image_to_data(
                pil_image, lang="fra+eng", output_type=pytesseract.Output.DICT
            )

            texts = []
            confidences = []

            for i, text in enumerate(data["text"]):
                if text.strip():
                    texts.append(text)
                    try:
                        conf = int(data["conf"][i])
                        if conf > 0:
                            confidences.append(conf / 100.0)
                    except:
                        pass

            # Reconstruct text with line breaks
            lines = {}
            for i, text in enumerate(data["text"]):
                if text.strip():
                    line_num = data["line_num"][i]
                    if line_num not in lines:
                        lines[line_num] = []
                    lines[line_num].append(text)

            sorted_lines = [" ".join(lines[k]) for k in sorted(lines.keys())]
            full_text = "\n".join(sorted_lines)

            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.5

            return full_text, avg_confidence

        except Exception as e:
            logger.error(f"Tesseract error: {e}")
            return "", 0.0

    def is_available(self) -> bool:
        """Check if any OCR engine is available."""
        return self.tesseract_available or self.easyocr_available

    def get_available_engines(self) -> List[str]:
        """Get list of available engines."""
        engines = []
        if self.tesseract_available:
            engines.append("tesseract")
        if self.easyocr_available:
            engines.append("easyocr")
        return engines
