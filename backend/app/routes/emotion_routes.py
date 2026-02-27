from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.emotion_model import EmotionLog

router = APIRouter(prefix="/emotion", tags=["Emotion"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/log")
def log_emotion(user_id: int, emotion: str, db: Session = Depends(get_db)):
    log = EmotionLog(user_id=user_id, emotion=emotion)
    db.add(log)
    db.commit()
    return {"message": "Emotion logged"}

@router.get("/timeline/{user_id}")
def emotion_timeline(user_id: int, db: Session = Depends(get_db)):
    logs = db.query(EmotionLog).filter(EmotionLog.user_id == user_id).all()
    return logs
