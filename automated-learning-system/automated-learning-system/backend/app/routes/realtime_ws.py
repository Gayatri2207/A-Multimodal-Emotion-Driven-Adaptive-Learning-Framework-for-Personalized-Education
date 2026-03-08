from fastapi import WebSocket, APIRouter
from app.services.adaptive_engine import get_adaptive_action

router = APIRouter()

@router.websocket("/ws/emotion")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    while True:
        data = await websocket.receive_json()

        emotion_score = float(data.get("emotion", 0.5))
        performance_score = float(data.get("performance", 0.5))

        action = get_adaptive_action(emotion_score, performance_score)

        await websocket.send_json({
            "emotion_score": emotion_score,
            "performance_score": performance_score,
            "adaptive_action": action
        })
