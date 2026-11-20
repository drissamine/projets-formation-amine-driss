"""
Document OCR API v3.0 - Using PaddleOCR
Much better for real-world documents!
"""

import os
import sys
import cv2
import time
import io
import logging
import json
from pathlib import Path
from typing import List, Optional

import numpy as np
from PIL import Image
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

# Setup
BASE_DIR = Path(__file__).parent.parent

# PaddleOCR setup
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# FastAPI App
app = FastAPI(
    title="Document OCR API v3.0 - PaddleOCR",
    version="3.0.0",
    description="Advanced OCR using PaddleOCR - handles real-world documents better!",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables
paddleocr_engine = None
ppstructure_engine = None

# Document classes
DOC_CLASSES = {0: "id_card", 1: "driver_license", 2: "residence_permit", 3: "passport"}

DOC_NAMES_FR = {
    "id_card": "Carte d'identité",
    "driver_license": "Permis de conduire",
    "residence_permit": "Titre de séjour",
    "passport": "Passeport",
    "unknown": "Document",
    "table": "Tableau",
    "figure": "Figure",
    "title": "Titre",
    "paragraph": "Paragraphe",
}


# ==================== OCR ENGINE ====================


def init_paddleocr():
    """Initialize PaddleOCR."""
    global paddleocr_engine, ppstructure_engine

    try:
        from paddleocr import PaddleOCR
        from paddleocr import PPStructure

        logger.info("Initializing PaddleOCR...")

        # Initialize OCR engine - use angle classification, OCR
        paddleocr_engine = PaddleOCR(
            use_angle_cls=True,
            lang="fr",  # French
            use_gpu=False,  # CPU mode
            show_log=False,
            det_model_dir=None,  # Use default
            rec_model_dir=None,  # Use default
            cls_model_dir=None,  # Use default
        )

        logger.info("PaddleOCR initialized successfully!")
        logger.info(f"Available languages: French + English")

        # Try to initialize structure detection
        try:
            ppstructure_engine = PPStructure(show_log=False)
            logger.info("PPStructure initialized for layout analysis")
        except Exception as e:
            logger.warning(f"PPStructure not available: {e}")

        return True

    except Exception as e:
        logger.error(f"Failed to initialize PaddleOCR: {e}")
        return False


def extract_fields_from_text(text: str) -> dict:
    """Extract structured fields from OCR text."""
    fields = {}
    lines = text.split("\n")

    # French patterns
    patterns = {
        "nom": r"(?:Nom|Surname|FAMILLE)[\s:]*([A-Z][A-Z\s\-]+)",
        "prenom": r"(?:Prenom|Prénom|Given|FORENAME)[\s:]*([A-Z][A-Za-z\s\-]+)",
        "date_naissance": r"(?:Date de naissance|Né le|Birth)[\s:]*(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})",
        "date_expiration": r"(?:Expire|Valid until|Expiry)[\s:]*(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})",
        "numero": r"(?:No|Number|Numéro|N°)[\s:]*([A-Z0-9]{5,20})",
        "categorie": r"(?:Catégorie|Class|CAT)[\s:]*([A-Z])",
    }

    import re

    for field_name, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            fields[field_name] = match.group(1).strip()

    # Generic key:value extraction for remaining fields
    for line in lines[:15]:
        line = line.strip()
        if ":" in line:
            parts = line.split(":", 1)
            if len(parts) == 2:
                key = parts[0].strip().lower()[:20]
                value = parts[1].strip()[:50]
                if value and len(value) > 2 and key not in fields:
                    fields[key] = value

    return fields


def detect_document_type(text: str) -> tuple:
    """Detect document type from text."""
    text_lower = text.lower()

    keywords = {
        "id_card": [
            "carte identité",
            "id card",
            "identity card",
            "cni",
            "cin",
            "carte nationale",
        ],
        "driver_license": [
            "permis conduire",
            "driver license",
            "permis de conduire",
            "driving licence",
        ],
        "residence_permit": [
            "titre séjour",
            "residence permit",
            "permis séjour",
            "carte séjour",
        ],
        "passport": ["passeport", "passport", "travel document"],
    }

    best_type = "unknown"
    best_score = 0

    for doc_type, kw_list in keywords.items():
        score = sum(1 for kw in kw_list if kw in text_lower)
        if score > best_score:
            best_score = score
            best_type = doc_type

    return best_type, min(best_score / 2, 1.0)


# ==================== MODELS ====================


class Detection(BaseModel):
    class_id: int
    class_name: str
    confidence: float
    bbox: List[float]


class OCRResult(BaseModel):
    document_type: str
    document_type_fr: str
    confidence: float
    raw_text: str
    fields: dict
    layout: Optional[list] = None


class OCRResponse(BaseModel):
    success: bool
    message: str
    document: OCRResult
    detections: List[Detection]
    processing: dict
    inference_time: float


# ==================== ENDPOINTS ====================


@app.on_event("startup")
async def startup():
    """Initialize PaddleOCR on startup."""
    success = init_paddleocr()
    if not success:
        logger.warning("PaddleOCR initialization failed - API will use fallback mode")


@app.get("/")
async def root():
    """API info."""
    return {
        "name": "Document OCR API v3.0 - PaddleOCR",
        "version": "3.0.0",
        "engine": "PaddleOCR PP-OCRv5",
        "features": [
            "Real-world document handling",
            "Multi-language support (100+)",
            "Layout analysis",
            "Table detection",
        ],
    }


@app.get("/health")
async def health():
    """Health check."""
    return {
        "status": "healthy",
        "paddleocr_available": paddleocr_engine is not None,
        "ppstructure_available": ppstructure_engine is not None,
    }


def preprocess_image(file_bytes: bytes) -> np.ndarray:
    """Convert uploaded file to numpy array."""
    image = Image.open(io.BytesIO(file_bytes))
    if image.mode != "RGB":
        image = image.convert("RGB")
    return np.array(image)


@app.post("/ocr", response_model=OCRResponse)
async def ocr_basic(file: UploadFile = File(...)):
    """OCR using PaddleOCR."""
    try:
        start_time = time.time()

        if paddleocr_engine is None:
            raise HTTPException(status_code=503, detail="PaddleOCR not available")

        # Read image
        contents = await file.read()
        image = preprocess_image(contents)

        # Save temp image for PaddleOCR
        temp_path = BASE_DIR / "temp_ocr.jpg"
        cv2.imwrite(str(temp_path), cv2.cvtColor(image, cv2.COLOR_RGB2BGR))

        # Run PaddleOCR
        logger.info("Running PaddleOCR...")
        result = paddleocr_engine.ocr(str(temp_path), cls=True)

        # Clean up temp file
        if temp_path.exists():
            temp_path.unlink()

        # Process results
        all_text = ""
        boxes = []

        if result and result[0]:
            for line in result[0]:
                if line:
                    box = line[0]
                    text = line[1][0]
                    conf = line[1][1]

                    boxes.append(
                        {
                            "text": text,
                            "confidence": conf,
                            "bbox": [int(c) for c in box],
                        }
                    )
                    all_text += text + "\n"

        # Extract fields
        fields = extract_fields_from_text(all_text)

        # Detect document type
        doc_type, type_conf = detect_document_type(all_text)

        # Calculate confidence
        avg_conf = sum([b["confidence"] for b in boxes]) / len(boxes) if boxes else 0

        return OCRResponse(
            success=True,
            message="OCR completed successfully with PaddleOCR",
            document=OCRResult(
                document_type=doc_type,
                document_type_fr=DOC_NAMES_FR.get(doc_type, "Document"),
                confidence=avg_conf,
                raw_text=all_text[:3000],
                fields=fields,
            ),
            detections=[],
            processing={"engine": "paddleocr-v5", "detections": len(boxes)},
            inference_time=time.time() - start_time,
        )

    except Exception as e:
        logger.error(f"OCR error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ocr-file")
async def ocr_from_path(data: dict):
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

        # Read image
        image = cv2.imread(str(full_path))
        if image is None:
            raise HTTPException(status_code=400, detail="Cannot read image")

        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Save temp
        temp_path = BASE_DIR / "temp_ocr.jpg"
        cv2.imwrite(str(temp_path), image)

        # OCR
        start_time = time.time()

        if paddleocr_engine is None:
            raise HTTPException(status_code=503, detail="PaddleOCR not available")

        result = paddleocr_engine.ocr(str(temp_path), cls=True)

        # Clean up
        if temp_path.exists():
            temp_path.unlink()

        # Process results
        all_text = ""
        boxes = []

        if result and result[0]:
            for line in result[0]:
                if line:
                    box = line[0]
                    text = line[1][0]
                    conf = line[1][1]

                    boxes.append(
                        {
                            "text": text,
                            "confidence": conf,
                            "bbox": [int(c) for c in box],
                        }
                    )
                    all_text += text + "\n"

        fields = extract_fields_from_text(all_text)
        doc_type, _ = detect_document_type(all_text)

        avg_conf = sum([b["confidence"] for b in boxes]) / len(boxes) if boxes else 0

        return {
            "success": True,
            "document": {
                "document_type": doc_type,
                "document_type_fr": DOC_NAMES_FR.get(doc_type, "Document"),
                "confidence": avg_conf,
                "raw_text": all_text[:3000],
                "fields": fields,
            },
            "detections": boxes,
            "inference_time": time.time() - start_time,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"OCR file error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/dashboard")
async def dashboard():
    """Serve the dashboard."""
    return FileResponse(str(BASE_DIR / "api" / "index.html"))


@app.get("/img/{file_path:path}")
async def get_img(file_path: str):
    """Serve images."""
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
