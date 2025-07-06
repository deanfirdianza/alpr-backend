# --- Add to your FastAPI backend ---
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from fastapi.responses import JSONResponse

router = APIRouter()

# Global flag for auto OCR mode
AUTO_OCR_ENABLED = False

class AutoOCRToggle(BaseModel):
    enabled: bool

@router.get("/auto_ocr")
def get_auto_ocr_status():
    return {"enabled": AUTO_OCR_ENABLED}

@router.post("/auto_ocr")
def set_auto_ocr_status(data: AutoOCRToggle):
    global AUTO_OCR_ENABLED
    AUTO_OCR_ENABLED = data.enabled
    return {"enabled": AUTO_OCR_ENABLED}
