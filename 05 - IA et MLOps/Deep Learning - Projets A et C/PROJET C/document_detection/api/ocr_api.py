# Windows OCR alternative using Windows.Media.Ocr (built into Windows 10/11)
# Falls back to basic detection

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from ultralytics import YOLO
import numpy as np
from PIL import Image
import io
import time
import cv2
import re
import json
import subprocess
from pathlib import Path
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="Document OCR API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).parent.parent
model = None


class DocumentFields(BaseModel):
    document_type: str
    raw_text: str
    fields: dict
    confidence: float
    bbox: Optional[list] = None


class OCRResponse(BaseModel):
    detections: list
    document: DocumentFields
    inference_time: float
    model: str


COCO_NAMES = {
    0: "person",
    1: "bicycle",
    2: "car",
    3: "motorcycle",
    4: "airplane",
    5: "bus",
    6: "train",
    7: "truck",
    8: "boat",
    9: "traffic light",
    10: "fire hydrant",
    11: "stop sign",
    12: "parking meter",
    13: "bench",
    14: "bird",
    15: "cat",
    16: "dog",
    17: "horse",
    18: "sheep",
    19: "cow",
    20: "elephant",
    21: "bear",
    22: "zebra",
    23: "giraffe",
    24: "backpack",
    25: "umbrella",
    26: "handbag",
    27: "tie",
    28: "suitcase",
    29: "frisbee",
    30: "skis",
    31: "snowboard",
    32: "sports ball",
    33: "kite",
    34: "baseball bat",
    35: "baseball glove",
    36: "skateboard",
    37: "surfboard",
    38: "tennis racket",
    39: "bottle",
    40: "wine glass",
    41: "cup",
    42: "fork",
    43: "knife",
    44: "spoon",
    45: "bowl",
    46: "banana",
    47: "apple",
    48: "sandwich",
    49: "orange",
    50: "broccoli",
    51: "carrot",
    52: "hot dog",
    53: "pizza",
    54: "donut",
    55: "cake",
    56: "chair",
    57: "couch",
    58: "potted plant",
    59: "bed",
    60: "dining table",
    61: "toilet",
    62: "tv",
    63: "laptop",
    64: "mouse",
    65: "remote",
    66: "keyboard",
    67: "cell phone",
    68: "microwave",
    69: "oven",
    70: "toaster",
    71: "sink",
    72: "refrigerator",
    73: "book",
    74: "clock",
    75: "vase",
    76: "scissors",
    77: "teddy bear",
    78: "hair drier",
    79: "toothbrush",
}

DOCUMENT_PATTERNS = {
    "id_card": {
        "keywords": [
            "identity",
            "carte",
            "national",
            "cin",
            "id card",
            "identite",
            "nationale",
            "carte d'identité",
        ],
        "fields": {
            "nom": r"(?:Nom|Surname|Family name)[:\s]*([A-ZÉÈÎÔÂÙÂ]+)",
            "prenom": r"(?:Prenom|prénom|First name|Given name)[:\s]*([A-ZÉÈÎÔÂÙÂ]+)",
            "date_naissance": r"(?:Date de naissance|DN|Dd?N|Date of birth)[:\s]*(\d{2}[/\-\.]\d{2}[/\-\.]\d{4})",
            "numero": r"(?:Numéro|Number|No|Number)[:\s]*([A-Z0-9]+)",
        },
    },
    "driver_license": {
        "keywords": [
            "driver",
            "permit",
            "conduire",
            "driving",
            "license",
            "permis",
            "conduire",
            "permis de conduire",
        ],
        "fields": {
            "nom": r"(?:Nom|Surname)[:\s]*([A-ZÉÈÎÔÂÙÂ]+)",
            "prenom": r"(?:Prenom|prénom)[:\s]*([A-ZÉÈÎÔÂÙÂ]+)",
            "date_naissance": r"(?:DDN|Date de naissance|Date of birth)[:\s]*(\d{2}[/\-\.]\d{2}[/\-\.]\d{4})",
            "date_expiration": r"(?:Expire|Valid|Vexpires|Expiry)[:\s]*(\d{2}[/\-\.]\d{2}[/\-\.]\d{4})",
            "categorie": r"(?:Catégorie|Category|Class)[:\s]*([A-Z])",
        },
    },
    "residence_permit": {
        "keywords": [
            "residence",
            "soggiorno",
            "sejour",
            "stay",
            "title",
            "titre",
            "permis de séjour",
        ],
        "fields": {
            "nom": r"(?:Nom|Family name|Surname)[:\s]*([A-ZÉÈÎÔÂÙÂ]+)",
            "prenom": r"(?:Prenom|Given name)[:\s]*([A-ZÉÈÎÔÂÙÂ]+)",
            "date_naissance": r"(?:Birth|Date of birth|Date de naissance)[:\s]*(\d{2}[/\-\.]\d{2}[/\-\.]\d{4})",
            "date_expiration": r"(?:Expire|Valid until|Date d'expiration)[:\s]*(\d{2}[/\-\.]\d{2}[/\-\.]\d{4})",
            "numero_titre": r"(?:Numéro|Title No|No)[:\s]*([A-Z0-9]+)",
        },
    },
    "passport": {
        "keywords": ["passeport", "passport", "biometric"],
        "fields": {
            "nom": r"(?:Nom|Surname|Family name)[:\s]*([A-ZÉÈÎÔÂÙÂ]+)",
            "prenom": r"(?:Prenom|Given names)[:\s]*([A-ZÉÈÎÔÂÙÂ\s]+)",
            "date_naissance": r"(?:Date de naissance|Date of birth)[:\s]*(\d{2}[/\-\.]\d{2}[/\-\.]\d{4})",
            "date_expiration": r"(?:Expire|Valid until)[:\s]*(\d{2}[/\-\.]\d{2}[/\-\.]\d{4})",
            "numero_passeport": r"(?:Passeport No|Passport No)[:\s]*([A-Z0-9]+)",
        },
    },
}

ocr_module = None


# Try to find Tesseract - use the newly installed version
import os

tesseract_cmds = [
    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
    r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    # Winget installs to AppData
    os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\WinGet\Packages\Tesseract"),
]

tesseract_cmd = None
for search_path in tesseract_cmds:
    if os.path.exists(search_path):
        tesseract_cmd = search_path
        tesseract_available = True
        print(f"Tesseract found: {search_path}")
        break
    elif os.path.isdir(search_path):
        # Search in directory
        try:
            for root, dirs, files in os.walk(search_path):
                if "tesseract.exe" in files:
                    tesseract_cmd = os.path.join(root, "tesseract.exe")
                    tesseract_available = True
                    print(f"Tesseract found: {tesseract_cmd}")
                    break
        except:
            pass

if tesseract_cmd:
    import pytesseract

    pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
else:
    print("Tesseract not found in standard locations")


@app.on_event("startup")
async def load_model():
    global model
    try:
        model = YOLO("yolov8m.pt")
        print("YOLOv8m loaded")
        print(f"Tesseract: {tesseract_cmd}")
    except Exception as e:
        print(f"Error: {e}")


def preprocess_image(file_bytes: bytes) -> np.ndarray:
    image = Image.open(io.BytesIO(file_bytes))
    if image.mode != "RGB":
        image = image.convert("RGB")
    return np.array(image)


def detect_document_type(text: str) -> str:
    if not text:
        return "document"

    text_lower = text.lower()
    max_matches = 0
    detected_type = "document"

    for doc_type, config in DOCUMENT_PATTERNS.items():
        matches = sum(1 for kw in config["keywords"] if kw in text_lower)
        if matches > max_matches:
            max_matches = matches
            detected_type = doc_type

    return detected_type


def extract_fields(text: str, doc_type: str) -> dict:
    if not text or doc_type == "document":
        # Extract any key:value pairs
        fields = {}
        lines = text.split("\n")
        for line in lines[:15]:
            line = line.strip()
            if ":" in line:
                parts = line.split(":", 1)
                if len(parts) == 2:
                    key = parts[0].strip()[:30]
                    val = parts[1].strip()[:50]
                    if val and len(val) > 1:
                        fields[f"field_{len(fields) + 1}"] = val
        return fields if fields else {"text": text[:200]}

    fields = {}
    config = DOCUMENT_PATTERNS.get(doc_type, {})

    for field_name, pattern in config.get("fields", {}).items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            fields[field_name] = match.group(1).strip()

    return fields


def perform_ocr_simple(image: np.ndarray) -> str:
    """Simple OCR - tries various methods"""

    # Try pytesseract if available
    if tesseract_cmd:
        try:
            import pytesseract

            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
            pil_image = Image.fromarray(image)
            text = pytesseract.image_to_string(pil_image, lang="fra+eng")
            return text
        except Exception as e:
            return f"Tesseract error: {str(e)}"

    # No OCR available - return message
    return "[OCR non disponible - Installez Tesseract depuis https://github.com/UB-Mannheim/tesseract/wiki]"


@app.get("/")
async def root():
    return {
        "status": "ok",
        "message": "Document OCR API",
        "tesseract": bool(tesseract_cmd),
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "ocr_available": bool(tesseract_cmd),
    }


@app.post("/ocr-file")
async def ocr_file(data: dict):
    if model is None:
        raise HTTPException(500, "Model not loaded")

    file_path = data.get("path", "")
    full_path = Path(file_path)

    if not full_path.exists():
        full_path = BASE_DIR / file_path
    if not full_path.exists():
        full_path = BASE_DIR.parent / file_path
    if not full_path.exists():
        raise HTTPException(404, f"File not found: {file_path}")

    try:
        start = time.time()

        # Load image
        image = cv2.imread(str(full_path))
        if image is None:
            raise HTTPException(400, "Cannot read image")
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Detect objects
        results = model(str(full_path), verbose=False, show=False)[0]

        detections = []
        boxes = results.boxes
        for i in range(len(boxes)):
            box = boxes[i]
            conf = float(box.conf[0])
            xyxy = box.xyxy[0].tolist()
            cls = int(box.cls[0])
            class_name = COCO_NAMES.get(cls, f"class_{cls}")
            detections.append(
                {"class_name": class_name, "confidence": conf, "bbox": xyxy}
            )

        # Perform OCR
        full_text = perform_ocr_simple(image_rgb)

        # Detect document type
        doc_type = detect_document_type(full_text)

        # Extract fields
        fields = extract_fields(full_text, doc_type)

        inference_time = time.time() - start

        return OCRResponse(
            detections=detections,
            document=DocumentFields(
                document_type=doc_type,
                raw_text=full_text[:3000],
                fields=fields,
                confidence=0.8 if tesseract_cmd else 0.5,
            ),
            inference_time=inference_time,
            model="yolov8m+tesseract" if tesseract_cmd else "yolov8m",
        )
    except Exception as e:
        raise HTTPException(400, str(e))


@app.post("/ocr")
async def ocr_upload(file: UploadFile = File(...)):
    if model is None:
        raise HTTPException(500, "Model not loaded")

    try:
        start = time.time()
        contents = await file.read()
        image = preprocess_image(contents)

        results = model(image, verbose=False, show=False)[0]

        detections = []
        boxes = results.boxes
        for i in range(len(boxes)):
            box = boxes[i]
            conf = float(box.conf[0])
            xyxy = box.xyxy[0].tolist()
            cls = int(box.cls[0])
            class_name = COCO_NAMES.get(cls, f"class_{cls}")
            detections.append(
                {"class_name": class_name, "confidence": conf, "bbox": xyxy}
            )

        full_text = perform_ocr_simple(image)
        doc_type = detect_document_type(full_text)
        fields = extract_fields(full_text, doc_type)

        inference_time = time.time() - start

        return OCRResponse(
            detections=detections,
            document=DocumentFields(
                document_type=doc_type,
                raw_text=full_text[:3000],
                fields=fields,
                confidence=0.8 if tesseract_cmd else 0.5,
            ),
            inference_time=inference_time,
            model="yolov8m+tesseract" if tesseract_cmd else "yolov8m",
        )
    except Exception as e:
        raise HTTPException(400, str(e))
