from fastapi import APIRouter
from pydantic import BaseModel
from sqlalchemy.orm import Session
import config
from database import SessionLocal
from models import ScanHistory, PlateRegistry
from datetime import datetime, date
from utils.alpr import detect_and_read_plate
import cv2

router = APIRouter()

class ScanResponse(BaseModel):
    plate_number: str
    formatted_plate: str
    confidence: float
    tax_status: str
    timestamp: datetime

@router.post("/scan", response_model=list[ScanResponse])
def scan():
    db: Session = SessionLocal()

    # Capture a single frame from IP camera
    cap = cv2.VideoCapture(config.CAMERA_URL)
    ret, frame = cap.read()
    cap.release()

    if not ret:
        return []

    detections = detect_and_read_plate(frame)
    print(f"Detections: {detections}")
    result = []

    for det in detections:
        plate_number = det["plate_number"]
        confidence = det["confidence"]

        plate = db.query(PlateRegistry).filter_by(plate_number=plate_number).first()

        if plate:
            tax_status = "Paid" if plate.expired_at >= date.today() else "Unpaid"
            plate.tax_status = tax_status
            plate.last_checked = datetime.utcnow()
        else:
            tax_status = "not found"

        history = ScanHistory(
            plate_number=plate_number,
            timestamp=datetime.utcnow(),
            confidence=str(confidence)
        )
        db.add(history)
        db.commit()

        result.append(ScanResponse(
            plate_number=plate_number,
            confidence=confidence,
            tax_status=tax_status,
            timestamp=history.timestamp
        ))

    db.close()
    return result
