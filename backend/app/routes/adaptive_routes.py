from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.performance_model import Performance
from app.services.adaptive_engine import get_adaptive_action
def adjust_difficulty(emotion: str, score: int) -> str:
    emotion_mapping = {
        "happy": 0.8,
        "neutral": 0.5,
        "sad": 0.2
    }
    emotion_score = emotion_mapping.get(emotion, 0.5)
    performance_score = score / 100.0
    return get_adaptive_action(emotion_score, performance_score)

router = APIRouter(prefix="/adaptive", tags=["Adaptive"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/update")
def update_performance(user_id: int, score: int, emotion: str, db: Session = Depends(get_db)):
    performance = Performance(user_id=user_id, score=score)
    db.add(performance)
    db.commit()
    action = adjust_difficulty(emotion, score)
    return {"adaptive_action": action}
