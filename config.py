import os

URL = 'http://192.168.0.2:8080'
CAMERA_URL = os.getenv("CAMERA_URL", f"{URL}/video")
CAMERA_IMG_URL = os.getenv("CAMERA_IMG_URL", f"{URL}/shot.jpg")
AUTO_OCR_ENABLED = os.getenv("AUTO_OCR_ENABLED", "false").lower() == "true"
CSV_PATH = os.getenv("CSV_PATH", "license-data.csv")
DB_URL = os.getenv("DB_URL", "postgresql://user:pass@localhost:5432/alpr")
