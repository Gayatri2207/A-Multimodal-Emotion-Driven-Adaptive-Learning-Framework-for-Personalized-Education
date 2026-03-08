from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database import Base


class EmotionLog(Base):
    __tablename__ = "emotion_logs"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    emotion_score = Column(Float, nullable=False)
    emotion_label = Column(String, nullable=True)   # e.g. "Frustrated", "Focused"
    performance_score = Column(Float, nullable=False)
    adaptive_action = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<EmotionLog(id={self.id}, label={self.emotion_label}, score={self.emotion_score}, action={self.adaptive_action})>"
