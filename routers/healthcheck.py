import cv2
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from fastapi.responses import JSONResponse

import config
from database import SessionLocal

router = APIRouter()

@router.get("/healthcheck")
def healthcheck():
    try:
        # Test camera and DB connection
        camera = cv2.VideoCapture(config.CAMERA_URL)
        if not camera.isOpened():
            raise RuntimeError("Camera not reachable")
        camera.release()

        # DB check
        with SessionLocal() as db:
            db.execute("SELECT 1")

        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
