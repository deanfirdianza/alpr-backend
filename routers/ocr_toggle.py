from fastapi import APIRouter
import config

router = APIRouter()
AUTO_OCR_FLAG = {"enabled": config.AUTO_OCR_ENABLED}

@router.post("/toggle-auto-ocr")
def toggle_auto_ocr(state: bool):
    AUTO_OCR_FLAG["enabled"] = state
    return {"auto_ocr_enabled": state}

@router.get("/auto-ocr-status")
def get_ocr_status():
    return {"auto_ocr_enabled": AUTO_OCR_FLAG["enabled"]}
