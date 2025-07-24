from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import scan, plates, history, ocr_toggle, websocket, auto_ocr, ocr_image, healthcheck
from stream import video_feed_app
import config

app = FastAPI(title="Smart ALPR Backend")


# Allow CORS for local frontend during development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ⚠️ Use ["http://localhost:3000"] for more security in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include endpoints
app.include_router(scan.router)
app.include_router(plates.router)
app.include_router(history.router)
app.include_router(ocr_toggle.router)
app.include_router(websocket.router)
app.include_router(auto_ocr.router)
app.include_router(ocr_image.router)
app.include_router(healthcheck.router)

# Video stream route
app.mount("/video_feed", video_feed_app)

# Auto OCR background task
if config.AUTO_OCR_ENABLED:
    start_auto_ocr(app)