from fastapi import APIRouter, WebSocket
import base64
import cv2
import numpy as np
import asyncio
from app.multimodal.facial_emotion.inference import predict_frame
from app.services.emotion_service import fuse_multimodal

router = APIRouter()

@router.websocket("/ws/realtime")
async def realtime_emotion(websocket: WebSocket):

    await websocket.accept()

    try:
        while True:
            data = await websocket.receive_text()

            img_bytes = base64.b64decode(data.split(",")[1])
            np_arr = np.frombuffer(img_bytes, np.uint8)
            frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

            facial_emotion = predict_frame(frame)

            speech_emotion = "neutral"
            typing_emotion = "neutral"

            final_emotion = fuse_multimodal(
                facial_emotion,
                speech_emotion,
                typing_emotion
            )

            await websocket.send_json({
                "facial": facial_emotion,
                "final": final_emotion
            })

    except Exception as e:
        print("WebSocket error:", e)
