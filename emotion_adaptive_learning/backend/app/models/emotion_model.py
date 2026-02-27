from sqlalchemy import Column, Integer, String, ForeignKey
from app.database import Base

class EmotionLog(Base):
    __tablename__ = "emotion_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    emotion = Column(String)
