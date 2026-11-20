"""
Document OCR API - Multi-OCR Version
Supports DocTR, EasyOCR, and fallback OCR engines
"""

import os
import sys
import cv2
import time
import io
import logging
from pathlib import Path
from typing import List, Optional, Union
from enum import Enum

import numpy as np
from PIL import Image
from fastapi import FastAPI, File, UploadFile, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from ultralytics import YOLO

BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR / "src"))

from ocr import DocumentPreprocessor, FieldExtractor

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Document OCR API - Multi-OCR",
    version="3.0.0",
    description="Advanced OCR with DocTR, EasyOCR support",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MODEL_PATH = BASE_DIR / "models" / "document_detector.pt"
model = None
preprocessor = None
field_extractor = None


# OCR Engine options
class OCREngineType(str, Enum):
    DOCTR = "doctr"
    EASYOCR = "easyocr"
    AUTO = "auto"


# Global OCR engines
doctr_model = None
easyocr_reader = None
current_ocr = None

DOC_CLASSES = {0: "id_card", 1: "driver_license", 2: "residence_permit", 3: "passport"}
DOC_NAMES_FR = {
    "id_card": "Carte d'identité",
    "driver_license": "Permis de conduire",
    "residence_permit": "Titre de séjour",
    "passport": "Passeport",
    "unknown": "Document inconnu",
}


class Detection(BaseModel):
    class_id: int
    class_name: str
    class_name_fr: str
    confidence: float
    bbox: List[float]


class OCRResult(BaseModel):
    document_type: str
    document_type_fr: str
    confidence: float
    raw_text: str
    fields: dict
    detection: Optional[dict] = None


class OCRResponse(BaseModel):
    success: bool
    message: str
    document: OCRResult
    detections: List[Detection]
    processing: dict
    inference_time: float
    ocr_engine: str


def load_yolo_model():
    global model
    if model is None:
        logger.info(f"Loading YOLO model from {MODEL_PATH}")
        model = YOLO(str(MODEL_PATH))
    return model


def init_doctr():
    global doctr_model
    if doctr_model is None:
        logger.info("Loading DocTR model...")
        from doctr.models import ocr_predictor

        doctr_model = ocr_predictor(pretrained=True)
        logger.info("DocTR loaded successfully")
    return doctr_model


def init_easyocr():
    global easyocr_reader
    if easyocr_reader is None:
        logger.info("Loading EasyOCR model...")
        from easyocr import Reader

        easyocr_reader = Reader(["fr", "en"], gpu=False)
        logger.info("EasyOCR loaded successfully")
    return easyocr_reader


def ocr_with_doctr(image: np.ndarray) -> str:
    """Run DocTR OCR on image."""
    from doctr.io import DocumentFile

    # Convert numpy array to bytes
    is_success, buffer = cv2.imencode(".png", image)
    if not is_success:
        return ""

    # Save to temporary file for DocTR
    import tempfile

    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        f.write(buffer.tobytes())
        temp_path = f.name

    try:
        doc = DocumentFile.from_images(temp_path)
        result = doctr_model(doc)
        text = result.render()
        return text
    finally:
        os.unlink(temp_path)


def ocr_with_easyocr(image: np.ndarray) -> str:
    """Run EasyOCR on image."""
    # EasyOCR needs RGB image
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    result = easyocr_reader.readtext(image_rgb)

    # Sort by position (top to bottom, left to right)
    lines = {}
    for bbox, text, conf in result:
        # Estimate line number from y-coordinate
        y = bbox[0][1]
        line_key = int(y / 50)  # Group by ~50 pixel rows
        if line_key not in lines:
            lines[line_key] = []
        lines[line_key].append((bbox[0][0], text))

    # Sort and join
    text_parts = []
    for line_key in sorted(lines.keys()):
        words = sorted(lines[line_key], key=lambda x: x[0])
        text_parts.append(" ".join([w[1] for w in words]))

    return "\n".join(text_parts)


def run_ocr(image: np.ndarray, engine: str = "auto") -> str:
    """Run OCR with specified or auto-detected engine."""
    global current_ocr

    if engine == "auto":
        # Try DocTR first (faster), fallback to EasyOCR
        try:
            init_doctr()
            return ocr_with_doctr(image)
        except Exception as e:
            logger.warning(f"DocTR failed: {e}, trying EasyOCR")
            try:
                init_easyocr()
                return ocr_with_easyocr(image)
            except Exception as e2:
                logger.error(f"EasyOCR also failed: {e2}")
                return ""

    elif engine == "doctr":
        init_doctr()
        return ocr_with_doctr(image)

    elif engine == "easyocr":
        init_easyocr()
        return ocr_with_easyocr(image)

    return ""


@app.on_event("startup")
async def startup():
    logger.info("Starting Document OCR API v3.0")
    load_yolo_model()
    preprocessor = DocumentPreprocessor()
    field_extractor = FieldExtractor()


@app.post("/ocr", response_model=OCRResponse)
async def process_document(
    file: UploadFile = File(...),
    ocr_engine: str = Query("auto", description="OCR engine: doctr, easyocr, auto"),
):
    start_time = time.time()

    try:
        # Read image
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if image is None:
            raise HTTPException(status_code=400, detail="Invalid image file")

        # Run YOLO detection
        yolo_model = load_yolo_model()
        results = yolo_model(image, conf=0.25, verbose=False)

        detections = []
        detected_doc = None
        best_conf = 0

        if (
            len(results) > 0
            and results[0].boxes is not None
            and len(results[0].boxes) > 0
        ):
            boxes = results[0].boxes

            for i in range(len(boxes)):
                box = boxes[i]
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])
                xyxy = box.xyxy[0].tolist()

                detection = Detection(
                    class_id=cls_id,
                    class_name=DOC_CLASSES.get(cls_id, "unknown"),
                    class_name_fr=DOC_NAMES_FR.get(
                        DOC_CLASSES.get(cls_id, "unknown"), "Unknown"
                    ),
                    confidence=conf,
                    bbox=xyxy,
                )
                detections.append(detection)

                if conf > best_conf:
                    best_conf = conf
                    detected_doc = detection

        # If no document detected, try to OCR entire image anyway
        if not detections:
            logger.info("No document detected, processing entire image")

        # Preprocess image
        if preprocessor is None:
            preprocessor = DocumentPreprocessor()

        # If we have a detection, crop to that region
        if detected_doc:
            x1, y1, x2, y2 = detected_doc.bbox
            h, w = image.shape[:2]
            x1, y1 = max(0, int(x1)), max(0, int(y1))
            x2, y2 = min(w, int(x2)), min(h, int(y2))
            processed = image[y1:y2, x1:x2]
        else:
            processed = image

        # Run OCR
        raw_text = run_ocr(processed, ocr_engine)

        # Extract fields
        if field_extractor is None:
            field_extractor = FieldExtractor()

        doc_type = detected_doc.class_name if detected_doc else "unknown"
        fields = field_extractor.extract(raw_text, doc_type)

        result = OCRResult(
            document_type=doc_type,
            document_type_fr=DOC_NAMES_FR.get(doc_type, "Unknown"),
            confidence=best_conf,
            raw_text=raw_text,
            fields=fields,
            detection=detected_doc.dict() if detected_doc else None,
        )

        inference_time = time.time() - start_time

        return OCRResponse(
            success=True,
            message="Document processed successfully",
            document=result,
            detections=detections,
            processing={
                "image_size": image.shape[:2],
                "preprocessing": "applied" if detections else "none",
            },
            inference_time=inference_time,
            ocr_engine=ocr_engine,
        )

    except Exception as e:
        logger.error(f"Error processing document: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/engines")
async def list_engines():
    """List available OCR engines."""
    return {
        "engines": [
            {
                "name": "doctr",
                "description": "DocTR - Fast and accurate",
                "type": "recommended",
            },
            {
                "name": "easyocr",
                "description": "EasyOCR - Good for complex layouts",
                "type": "fallback",
            },
            {
                "name": "auto",
                "description": "Auto-select best available",
                "type": "default",
            },
        ]
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "3.0.0"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
