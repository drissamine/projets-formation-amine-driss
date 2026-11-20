"""
Document OCR API - Improved Version
With proper document detection, preprocessing, and OCR
"""

import os
import sys
import cv2
import time
import io
import logging
from pathlib import Path
from typing import List, Optional

import numpy as np
from PIL import Image
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field
from ultralytics import YOLO

# Add src to path for OCR module
BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR / "src"))

from ocr import DocumentPreprocessor, OCREngine, FieldExtractor

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# FastAPI App
app = FastAPI(
    title="Document OCR API - Improved",
    version="2.0.0",
    description="Advanced OCR for document detection with preprocessing",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Globals
MODEL_PATH = BASE_DIR / "models" / "document_detector.pt"
model = None
preprocessor = None
ocr_engine = None
field_extractor = None

# Document class names (must match training)
DOC_CLASSES = {0: "id_card", 1: "driver_license", 2: "residence_permit", 3: "passport"}

DOC_NAMES_FR = {
    "id_card": "Carte d'identité",
    "driver_license": "Permis de conduire",
    "residence_permit": "Titre de séjour",
    "passport": "Passeport",
    "unknown": "Document inconnu",
}


# Pydantic Models
class Detection(BaseModel):
    class_id: int
    class_name: str
    class_name_fr: str
    confidence: float
    bbox: List[float]


class ExtractedField(BaseModel):
    key: str
    value: str
    label: str


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


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    ocr_available: bool
    ocr_engines: List[str]
    version: str = "2.0.0"


@app.on_event("startup")
async def load_model():
    """Load model and OCR components on startup."""
    global model, preprocessor, ocr_engine, field_extractor

    try:
        # Load YOLO model
        if MODEL_PATH.exists():
            model = YOLO(str(MODEL_PATH))
            logger.info(f"Loaded document detector model: {MODEL_PATH}")
        else:
            # Fallback to yolov8n for testing
            logger.warning(f"Model not found at {MODEL_PATH}, using yolov8n")
            model = YOLO("yolov8n.pt")

        # Initialize OCR components
        preprocessor = DocumentPreprocessor(target_width=1024)
        ocr_engine = OCREngine(preferred_engine="auto")
        field_extractor = FieldExtractor()

        logger.info("OCR components initialized")
        logger.info(f"Available OCR engines: {ocr_engine.get_available_engines()}")

    except Exception as e:
        logger.error(f"Error during startup: {e}")
        raise


def preprocess_image(file_bytes: bytes) -> np.ndarray:
    """Convert uploaded file to numpy array."""
    image = Image.open(io.BytesIO(file_bytes))
    if image.mode != "RGB":
        image = image.convert("RGB")
    return np.array(image)


def detect_documents(image: np.ndarray, conf_threshold: float = 0.25) -> List[dict]:
    """Run YOLO detection and return document detections."""
    if model is None:
        raise HTTPException(status_code=500, detail="Model not loaded")

    results = model(image, verbose=False, conf=conf_threshold)[0]

    detections = []
    for box in results.boxes:
        cls_id = int(box.cls[0])
        confidence = float(box.conf[0])
        bbox = box.xyxy[0].tolist()

        class_name = DOC_CLASSES.get(cls_id, f"class_{cls_id}")

        detections.append(
            {
                "class_id": cls_id,
                "class_name": class_name,
                "confidence": confidence,
                "bbox": [int(c) for c in bbox],
            }
        )

    # Sort by confidence
    detections.sort(key=lambda x: x["confidence"], reverse=True)
    return detections


def process_document(
    image: np.ndarray, detection: dict, use_preprocessing: bool = True
) -> dict:
    """
    Process a single document detection with OCR.

    Args:
        image: Full image
        detection: Detection dict with bbox
        use_preprocessing: Whether to apply image preprocessing

    Returns:
        Dict with OCR results
    """
    bbox = detection["bbox"]

    # Crop document region
    cropped = preprocessor.crop_document(image, bbox)

    # Preprocess for OCR
    if use_preprocessing:
        processed = preprocessor.preprocess(cropped)
    else:
        processed = cropped

    # Run OCR
    text, ocr_conf = ocr_engine.recognize(processed)

    # Detect document type from text
    doc_type, type_conf = field_extractor.detect_document_type(text)

    # Override with YOLO detection if confident
    if detection["confidence"] > 0.3:
        doc_type = detection["class_name"]

    # Extract fields
    fields = field_extractor.extract_fields(text, doc_type)

    return {
        "document_type": doc_type,
        "document_type_fr": DOC_NAMES_FR.get(doc_type, "Document"),
        "confidence": (ocr_conf + detection["confidence"]) / 2,
        "raw_text": text,
        "fields": fields,
        "ocr_confidence": ocr_conf,
        "detection": detection,
    }


def process_full_image(image: np.ndarray, use_preprocessing: bool = True) -> dict:
    """
    Fallback: Process entire image when no document detected.

    Args:
        image: Full image
        use_preprocessing: Whether to apply image preprocessing

    Returns:
        Dict with OCR results
    """
    # Preprocess for OCR
    if use_preprocessing:
        processed = preprocessor.preprocess(image)
    else:
        processed = image

    # Run OCR
    text, ocr_conf = ocr_engine.recognize(processed)

    # Detect document type from text
    doc_type, type_conf = field_extractor.detect_document_type(text)

    # Extract fields
    fields = field_extractor.extract_fields(text, doc_type)

    return {
        "document_type": doc_type,
        "document_type_fr": DOC_NAMES_FR.get(doc_type, "Document"),
        "confidence": ocr_conf,
        "raw_text": text,
        "fields": fields,
        "ocr_confidence": ocr_conf,
        "detection": None,
    }


@app.get("/", response_model=dict)
async def root():
    """API info endpoint."""
    return {
        "name": "Document OCR API - Improved",
        "version": "2.0.0",
        "endpoints": {
            "/": "This info",
            "/health": "Health check",
            "/detect": "Detect documents in image",
            "/ocr": "Full OCR processing",
            "/ocr-smart": "Smart OCR with preprocessing",
            "/dashboard": "Web UI",
        },
    }


@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        model_loaded=model is not None,
        ocr_available=ocr_engine.is_available() if ocr_engine else False,
        ocr_engines=ocr_engine.get_available_engines() if ocr_engine else [],
    )


@app.post("/detect", response_model=dict)
async def detect(file: UploadFile = File(...), conf: float = 0.5):
    """Detect documents in uploaded image."""
    try:
        contents = await file.read()
        image = preprocess_image(contents)

        start_time = time.time()
        detections = detect_documents(image, conf)
        inference_time = time.time() - start_time

        # Format response
        results = []
        for det in detections:
            results.append(
                Detection(
                    class_id=det["class_id"],
                    class_name=det["class_name"],
                    class_name_fr=DOC_NAMES_FR.get(
                        det["class_name"], det["class_name"]
                    ),
                    confidence=det["confidence"],
                    bbox=det["bbox"],
                )
            )

        return {
            "success": True,
            "detections": results,
            "count": len(results),
            "inference_time": inference_time,
        }

    except Exception as e:
        logger.error(f"Detection error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ocr", response_model=OCRResponse)
async def ocr_basic(file: UploadFile = File(...)):
    """Basic OCR without preprocessing (fast)."""
    try:
        start_time = time.time()
        contents = await file.read()
        image = preprocess_image(contents)

        # Detect documents
        detections = detect_documents(image)

        if not detections:
            # Fallback: process entire image
            logger.info("No document detected, processing full image")
            result = process_full_image(image, use_preprocessing=False)

            return OCRResponse(
                success=True,
                message="OCR completed (full image - no document detected)",
                document=OCRResult(**result),
                detections=[],
                processing={
                    "preprocessing": False,
                    "engine": ocr_engine.get_available_engines()[0]
                    if ocr_engine.is_available()
                    else "none",
                },
                inference_time=time.time() - start_time,
            )

        # Process best detection
        best_det = detections[0]
        result = process_document(image, best_det, use_preprocessing=False)

        # Format detections
        det_results = [
            Detection(
                class_id=d["class_id"],
                class_name=d["class_name"],
                class_name_fr=DOC_NAMES_FR.get(d["class_name"], d["class_name"]),
                confidence=d["confidence"],
                bbox=d["bbox"],
            )
            for d in detections
        ]

        return OCRResponse(
            success=True,
            message="OCR completed successfully",
            document=OCRResult(**result),
            detections=det_results,
            processing={
                "preprocessing": False,
                "engine": ocr_engine.get_available_engines()[0]
                if ocr_engine.is_available()
                else "none",
            },
            inference_time=time.time() - start_time,
        )

    except Exception as e:
        logger.error(f"OCR error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ocr-smart", response_model=OCRResponse)
async def ocr_smart(file: UploadFile = File(...)):
    """
    Smart OCR with full preprocessing pipeline.
    Best quality but slower.
    """
    try:
        start_time = time.time()
        contents = await file.read()
        image = preprocess_image(contents)

        # Detect documents
        detections = detect_documents(image)

        if not detections:
            return OCRResponse(
                success=False,
                message="No document detected",
                document=OCRResult(
                    document_type="unknown",
                    document_type_fr="Aucun document détecté",
                    confidence=0.0,
                    raw_text="",
                    fields={},
                ),
                detections=[],
                processing={"preprocessing": True, "engine": "none"},
                inference_time=time.time() - start_time,
            )

        # Process with preprocessing
        best_det = detections[0]
        result = process_document(image, best_det, use_preprocessing=True)

        # Format detections
        det_results = [
            Detection(
                class_id=d["class_id"],
                class_name=d["class_name"],
                class_name_fr=DOC_NAMES_FR.get(d["class_name"], d["class_name"]),
                confidence=d["confidence"],
                bbox=d["bbox"],
            )
            for d in detections
        ]

        return OCRResponse(
            success=True,
            message="Smart OCR completed successfully",
            document=OCRResult(**result),
            detections=det_results,
            processing={
                "preprocessing": True,
                "engine": ocr_engine.get_available_engines()[0]
                if ocr_engine.is_available()
                else "none",
            },
            inference_time=time.time() - start_time,
        )

    except Exception as e:
        logger.error(f"Smart OCR error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ocr-file")
async def ocr_file(data: dict):
    """OCR from file path."""
    try:
        file_path = data.get("path", "")
        full_path = Path(file_path)

        # Try multiple locations
        if not full_path.exists():
            full_path = BASE_DIR / file_path
        if not full_path.exists():
            full_path = BASE_DIR.parent / file_path
        if not full_path.exists():
            raise HTTPException(status_code=404, detail=f"File not found: {file_path}")

        # Load image
        image = cv2.imread(str(full_path))
        if image is None:
            raise HTTPException(status_code=400, detail="Cannot read image")

        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Create UploadFile-like object
        is_success, buffer = cv2.imencode(".jpg", image)
        if not is_success:
            raise HTTPException(status_code=500, detail="Failed to encode image")

        # Create fake UploadFile
        from fastapi import UploadFile

        fake_file = UploadFile(filename="image.jpg", file=io.BytesIO(buffer.tobytes()))

        # Call smart OCR
        return await ocr_smart(fake_file)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"File OCR error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/dashboard")
async def dashboard():
    """Serve the OCR dashboard."""
    return FileResponse(str(BASE_DIR / "api" / "ocr_dashboard.html"))


@app.get("/img/{file_path:path}")
async def get_img(file_path: str):
    """Serve images from dataset."""
    for prefix in [
        "",
        "dataset/images/",
        "dataset/images/train/",
        "dataset/images/val/",
    ]:
        test_path = BASE_DIR / prefix / file_path
        if test_path.exists():
            return FileResponse(str(test_path))
    return JSONResponse(status_code=404, content={"error": "File not found"})


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
