from fastapi import APIRouter, WebSocket
import cv2
import asyncio
from app.multimodal.facial_emotion.inference import predict_frame

router = APIRouter()

@router.websocket("/ws/emotion")
async def websocket_emotion(websocket: WebSocket):

    await websocket.accept()

    cap = cv2.VideoCapture(0)

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            emotion = predict_frame(frame)

            await websocket.send_json({
                "emotion": emotion
            })

            await asyncio.sleep(0.1)

    except Exception as e:
        print("WebSocket Error:", e)

    finally:
        cap.release()
        await websocket.close()
