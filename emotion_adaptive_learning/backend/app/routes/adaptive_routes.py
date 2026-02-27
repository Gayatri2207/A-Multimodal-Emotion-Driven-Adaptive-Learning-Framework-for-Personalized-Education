from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.performance_model import Performance
from app.services.adaptive_engine import adjust_difficulty

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
