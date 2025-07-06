import cv2
import re
import time
import numpy as np
from datetime import date
from ultralytics import YOLO
import easyocr

# Configs
MODEL_PATH = "best.pt"
OCR_LANGS = ['en']
CONF_THRESHOLD = 0.4
OCR_COOLDOWN = 1.5

# Load once
model = YOLO(MODEL_PATH)
reader = easyocr.Reader(OCR_LANGS)

# Cache to prevent re-OCR
last_ocr_time = {}
ocr_cache = {}

def clean_ocr_text(raw_text):
    text = raw_text.upper().replace(" ", "")
    if (dot_match := re.search(r"(\d{2})\.(\d{2})", text)):
        text = text.replace(dot_match.group(0), "")
    if (match := re.match(r"([A-Z]{1,2})(\d{5,})([A-Z]{1,3})", text)):
        prefix, digits, suffix = match.groups()
        text = prefix + digits[:4] + suffix
    return text

def extract_plate_number(text):
    match = re.search(r'[A-Z]{1,2}\d{1,4}[A-Z]{0,3}', text)
    return match.group() if match else "N/A"

def detect_and_read_plate(frame):
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = model(frame_rgb, verbose=False)[0]
    detections = []

    for box in results.boxes:
        conf = float(box.conf)
        if conf < CONF_THRESHOLD:
            continue

        x1, y1, x2, y2 = map(int, box.xyxy[0].cpu().numpy())
        cropped = frame[y1:y2, x1:x2]
        crop_key = (x1, y1, x2, y2)
        now = time.time()

        if crop_key in last_ocr_time and (now - last_ocr_time[crop_key] < OCR_COOLDOWN):
            plate_number = ocr_cache.get(crop_key, "N/A")
        else:
            result = reader.readtext(cropped)
            texts = [text.strip().upper().replace(" ", "") for _, text, _ in result if not (text.isdigit() and len(text) <= 2)]
            combined = ''.join(texts)
            cleaned = clean_ocr_text(combined)
            plate_number = extract_plate_number(cleaned)

            ocr_cache[crop_key] = plate_number
            last_ocr_time[crop_key] = now

        detections.append({
            "plate_number": plate_number,
            "bbox": (x1, y1, x2, y2),
            "confidence": round(conf, 2)
        })

    return detections
