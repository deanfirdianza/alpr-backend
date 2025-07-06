from fastapi import APIRouter, FastAPI, HTTPException
from ultralytics import YOLO
from datetime import datetime
import config
# from scan import scan_frame
import easyocr
import cv2
import numpy as np
import re
import os

router = APIRouter()

@router.get("/scan_by_image")
def scanByImage():
    try:
        result = scan_frame()
        if not result["plate_number"]:
            return {"message": "No valid plate detected.", **result}
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

MODEL_PATH = "best.pt"
OCR_LANGS = ['en']
CONF_THRESHOLD = 0.4

model = YOLO(MODEL_PATH)
reader = easyocr.Reader(OCR_LANGS)

def clean_ocr_text(raw_text: str) -> str:
    text = raw_text.upper().replace(" ", "")
    dot_match = re.search(r"(\d{2})\.(\d{2})", text)
    if dot_match:
        text = text.replace(dot_match.group(0), "")
    match = re.match(r"([A-Z]{1,2})(\d{5,})([A-Z]{1,3})", text)
    if match:
        prefix, digits, suffix = match.groups()
        text = prefix + digits[:4] + suffix
    return text

def scan_frame() -> dict:
    temp_filename = f"frame_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"

    # Download snapshot
    cap = cv2.VideoCapture(config.CAMERA_URL)
    ret, frame = cap.read()
    cap.release()

    if not ret or frame is None:
        raise RuntimeError("Failed to capture image from video feed.")

    cv2.imwrite(temp_filename, frame)

    # Run YOLO detection
    image = cv2.imread(temp_filename)
    results = model(image)[0]

    for box in results.boxes:
        conf = float(box.conf)
        if conf < CONF_THRESHOLD:
            continue
        x1, y1, x2, y2 = map(int, box.xyxy[0].cpu().numpy())
        cropped = image[y1:y2, x1:x2]
        ocr_result = reader.readtext(cropped)

        ocr_texts = []
        for bbox, text, _ in sorted(ocr_result, key=lambda x: x[0][0][0]):
            cleaned = text.strip().upper().replace(" ", "")
            if cleaned.isdigit() and len(cleaned) <= 2:
                continue
            ocr_texts.append(cleaned)

        combined = ''.join(ocr_texts)
        cleaned_text = clean_ocr_text(combined)
        plate_match = re.search(r'[A-Z]{1,2}\d{1,4}[A-Z]{0,3}', cleaned_text)
        plate_number = plate_match.group() if plate_match else None

        os.remove(temp_filename)

        return {
            "plate_number": plate_number,
            "confidence": round(conf, 4),
        }

    os.remove(temp_filename)
    return {"plate_number": None, "confidence": 0.0}
