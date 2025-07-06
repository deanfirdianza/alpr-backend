from fastapi import APIRouter, WebSocket

router = APIRouter()

@router.websocket("/ws/detections")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_text("🔌 WebSocket is live (but not implemented yet)")
