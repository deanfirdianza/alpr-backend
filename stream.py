from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import cv2
import config

video_feed_app = FastAPI()

def gen_frames():
    cap = cv2.VideoCapture(config.CAMERA_URL)
    while True:
        success, frame = cap.read()
        if not success:
            break
        _, buffer = cv2.imencode('.jpg', frame)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

@video_feed_app.get("/")
def video_feed():
    return StreamingResponse(gen_frames(), media_type="multipart/x-mixed-replace; boundary=frame")
