from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from app.database import get_db
from sqlalchemy.orm import Session
from app.schemas import EmotionIn
from app.services.rl_engine import rl_engine
from app.models.emotion_log import EmotionLog
from app.multimodal.fusion import weighted_fusion
import json

router = APIRouter()


@router.websocket("/ws/emotion")
async def emotion_ws(websocket: WebSocket, db: Session = Depends(get_db)):
    await websocket.accept()
    try:
        while True:
            text = await websocket.receive_text()
            try:
                payload = json.loads(text)
            except Exception:
                await websocket.send_json({"error": "invalid_json"})
                continue

            # accept either fused emotion_score or separate modality scores
            facial = payload.get("facial_score")
            speech = payload.get("speech_score")
            typing = payload.get("typing_score")
            emotion_score = payload.get("emotion_score")
            performance_score = payload.get("performance_score")

            if emotion_score is None:
                # run fusion if individual modalities provided
                fused = weighted_fusion(facial, speech, typing)
                emotion_score = float(fused)
            else:
                emotion_score = float(emotion_score)

            performance_score = float(performance_score) if performance_score is not None else 0.5

            action = rl_engine.get_adaptive_action(float(emotion_score), float(performance_score))

            # persist log
            log = EmotionLog(user_id=None, emotion_score=float(emotion_score), performance_score=float(performance_score), adaptive_action=action)
            db.add(log)
            db.commit()
            db.refresh(log)

            await websocket.send_json({"adaptive_action": action, "emotion_score": emotion_score, "performance_score": performance_score})
    except WebSocketDisconnect:
        return
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
