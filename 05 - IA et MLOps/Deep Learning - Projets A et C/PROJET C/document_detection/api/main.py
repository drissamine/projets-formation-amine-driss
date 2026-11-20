from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from ultralytics import YOLO
import numpy as np
from PIL import Image
import io
import time
from pathlib import Path
from pydantic import BaseModel
from typing import List

app = FastAPI(title="Document Detection API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).parent.parent
model = None


class Detection(BaseModel):
    class_name: str
    confidence: float
    bbox: List[float]


class DetectionResponse(BaseModel):
    detections: List[Detection]
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


@app.on_event("startup")
async def load_model():
    global model
    try:
        model = YOLO("yolov8m.pt")
        print("YOLOv8m loaded")
    except Exception as e:
        print(f"Error: {e}")


def preprocess_image(file_bytes: bytes) -> np.ndarray:
    image = Image.open(io.BytesIO(file_bytes))
    if image.mode != "RGB":
        image = image.convert("RGB")
    return np.array(image)


import cv2
import re
import os

TESSERACT_CMD = None
tesseract_cmds = [
    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
    r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
]
for search_path in tesseract_cmds:
    if os.path.exists(search_path):
        TESSERACT_CMD = search_path
        break

if TESSERACT_CMD:
    import pytesseract

    pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD


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
        ],
        "fields": {
            "nom": r"(?:Nom|Surname|Family name)[:\s]*([A-ZÉÈÎÔÂÙÂ]+)",
            "prenom": r"(?:Prenom|prénom|First name)[:\s]*([A-ZÉÈÎÔÂÙÂ]+)",
            "date_naissance": r"(?:Date de naissance|DN|Dd?N)[:\s]*(\d{2}[/\-\.]\d{2}[/\-\.]\d{4})",
            "numero": r"(?:Numéro|Number|No)[:\s]*([A-Z0-9]+)",
        },
    },
    "driver_license": {
        "keywords": ["driver", "permit", "conduire", "driving", "license", "permis"],
        "fields": {
            "nom": r"(?:Nom|Surname)[:\s]*([A-ZÉÈÎÔÂÙÂ]+)",
            "prenom": r"(?:Prenom|prénom)[:\s]*([A-ZÉÈÎÔÂÙÂ]+)",
            "date_naissance": r"(?:DDN|Date de naissance)[:\s]*(\d{2}[/\-\.]\d{2}[/\-\.]\d{4})",
            "categorie": r"(?:Catégorie|Category|Class)[:\s]*([A-Z])",
        },
    },
    "passport": {
        "keywords": ["passeport", "passport", "biometric"],
        "fields": {
            "nom": r"(?:Nom|Surname|Family name)[:\s]*([A-ZÉÈÎÔÂÙÂ]+)",
            "prenom": r"(?:Prenom|Given names)[:\s]*([A-ZÉÈÎÔÂÙÂ\s]+)",
            "numero_passeport": r"(?:Passeport No|Passport No)[:\s]*([A-Z0-9]+)",
        },
    },
}


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


def perform_ocr(image: np.ndarray) -> str:
    if TESSERACT_CMD:
        try:
            pil_image = Image.fromarray(image)
            return pytesseract.image_to_string(pil_image, lang="fra+eng")
        except Exception as e:
            return f"OCR Error: {str(e)}"
    return "[OCR non disponible]"


# OCR endpoint
from fastapi import File, UploadFile


class DocumentFields(BaseModel):
    document_type: str
    raw_text: str
    fields: dict
    confidence: float


class OCRResponse(BaseModel):
    detections: list
    document: DocumentFields
    inference_time: float
    model: str


@app.post("/ocr")
async def ocr_full(file: UploadFile = File(...)):
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

        full_text = perform_ocr(image)
        doc_type = detect_document_type(full_text)
        fields = extract_fields(full_text, doc_type)

        return OCRResponse(
            detections=detections[:10],
            document=DocumentFields(
                document_type=doc_type,
                raw_text=full_text[:3000],
                fields=fields,
                confidence=0.8 if TESSERACT_CMD else 0.5,
            ),
            inference_time=time.time() - start,
            model="yolov8m+tesseract" if TESSERACT_CMD else "yolov8m",
        )
    except Exception as e:
        raise HTTPException(400, str(e))


@app.post("/ocr-file")
async def ocr_file_full(data: dict):
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
        image = cv2.imread(str(full_path))
        if image is None:
            raise HTTPException(400, "Cannot read image")
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

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

        full_text = perform_ocr(image_rgb)
        doc_type = detect_document_type(full_text)
        fields = extract_fields(full_text, doc_type)

        return OCRResponse(
            detections=detections[:10],
            document=DocumentFields(
                document_type=doc_type,
                raw_text=full_text[:3000],
                fields=fields,
                confidence=0.8 if TESSERACT_CMD else 0.5,
            ),
            inference_time=time.time() - start,
            model="yolov8m+tesseract" if TESSERACT_CMD else "yolov8m",
        )
    except Exception as e:
        raise HTTPException(400, str(e))


@app.get("/")
async def root():
    return {
        "status": "ok",
        "message": "Document OCR API",
        "endpoints": {
            "/detect": "Object detection",
            "/detect-file": "Object detection by file path",
            "/ocr": "Full OCR + detection (upload)",
            "/ocr-file": "Full OCR + detection (path)",
            "/dashboard": "Web UI",
        },
    }


@app.get("/dashboard")
async def dashboard():
    return FileResponse(str(Path(__file__).parent / "ocr_dashboard.html"))


@app.get("/ocr-ui")
async def ocr_ui():
    from fastapi.responses import FileResponse

    return FileResponse(str(Path(__file__).parent / "ocr_dashboard.html"))


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "ocr_available": TESSERACT_CMD is not None,
    }


@app.get("/img/{file_path:path}")
async def get_img(file_path: str):
    for prefix in ["", "dataset/images/"]:
        test_path = BASE_DIR / prefix / file_path
        if test_path.exists():
            return FileResponse(str(test_path))
    return {"error": "File not found"}


@app.post("/detect-file")
async def detect_file(data: dict):
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
        results = model(str(full_path), verbose=False, show=False)[0]
        inference_time = time.time() - start

        detections = []
        boxes = results.boxes
        for i in range(len(boxes)):
            box = boxes[i]
            conf = float(box.conf[0])
            xyxy = box.xyxy[0].tolist()
            cls = int(box.cls[0])
            class_name = COCO_NAMES.get(cls, f"class_{cls}")
            detections.append(
                Detection(
                    class_name=class_name,
                    confidence=conf,
                    bbox=xyxy,
                )
            )

        detections.sort(key=lambda x: x.confidence, reverse=True)

        return DetectionResponse(
            detections=detections[:10],
            inference_time=inference_time,
            model="yolov8m-pretrained",
        )
    except Exception as e:
        raise HTTPException(400, str(e))


@app.post("/detect")
async def detect(file: UploadFile = File(...)):
    if model is None:
        raise HTTPException(500, "Model not loaded")

    try:
        contents = await file.read()
        image = preprocess_image(contents)

        start = time.time()
        results = model(image, verbose=False, show=False)[0]
        inference_time = time.time() - start

        detections = []
        boxes = results.boxes
        for i in range(len(boxes)):
            box = boxes[i]
            conf = float(box.conf[0])
            xyxy = box.xyxy[0].tolist()
            cls = int(box.cls[0])
            class_name = COCO_NAMES.get(cls, f"class_{cls}")
            detections.append(
                Detection(
                    class_name=class_name,
                    confidence=conf,
                    bbox=xyxy,
                )
            )

        detections.sort(key=lambda x: x.confidence, reverse=True)

        return DetectionResponse(
            detections=detections[:10],
            inference_time=inference_time,
            model="yolov8m-pretrained",
        )
    except Exception as e:
        raise HTTPException(400, str(e))
