from fastapi import APIRouter, FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import datetime, date, timezone
from ultralytics import YOLO
from database import SessionLocal
from routers.scan import ScanResponse
from models import PlateRegistry, ScanHistory
import config
import easyocr
import cv2
import numpy as np
import re
import os

router = APIRouter()

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

def format_plate(plate: str) -> str:
    match = re.match(r"^([A-Z]{1,2})(\d{1,4})([A-Z]{0,3})$", plate)
    if not match:
        return plate
    prefix, number, suffix = match.groups()
    parts = [prefix, number]
    if suffix:
        parts.append(suffix)
    return "-".join(parts)

def scan_frame() -> list:
    db: Session = SessionLocal()
    temp_filename = f"frame_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"

    cap = cv2.VideoCapture(config.CAMERA_URL)
    ret, frame = cap.read()
    cap.release()

    if not ret or frame is None:
        raise RuntimeError("Failed to capture image from video feed.")

    cv2.imwrite(temp_filename, frame)
    image = cv2.imread(temp_filename)
    results = model(image)[0]

    result = []
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

        if not plate_number:
            continue

        formatted_plate = format_plate(plate_number)
        plate = db.query(PlateRegistry).filter_by(plate_number=formatted_plate).first()

        if plate:
            tax_status = "Lunas" if plate.expired_at >= date.today() else "Belum Lunas"
            plate.tax_status = tax_status
            plate.last_checked = datetime.now(timezone.utc)
        else:
            tax_status = "Not Found"

        history = ScanHistory(
            plate_number=formatted_plate,
            timestamp=datetime.now(timezone.utc),
            confidence=str(conf),
        )
        db.add(history)
        db.commit()

        result.append(ScanResponse(
            plate_number=plate_number,
            formatted_plate=formatted_plate,
            confidence=conf,
            tax_status=tax_status,
            timestamp=history.timestamp,
        ))

    os.remove(temp_filename)
    return result[0]

@router.get("/scan_by_image")
def scanByImage():
    try:
        results = scan_frame()
        if not results:
            return {"message": "No valid plate detected."}
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
