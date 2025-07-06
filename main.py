from fastapi import FastAPI
from routers import scan, plates, history, ocr_toggle, websocket
from stream import video_feed_app
from auto_ocr import start_auto_ocr
import config

app = FastAPI(title="Smart ALPR Backend")

# Include endpoints
app.include_router(scan.router)
app.include_router(plates.router)
app.include_router(history.router)
app.include_router(ocr_toggle.router)
app.include_router(websocket.router)

# Video stream route
app.mount("/video_feed", video_feed_app)

# Auto OCR background task
if config.AUTO_OCR_ENABLED:
    start_auto_ocr(app)
