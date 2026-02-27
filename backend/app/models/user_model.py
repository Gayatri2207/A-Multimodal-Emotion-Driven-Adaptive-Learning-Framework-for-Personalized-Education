from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from ..database import Base


try:
    class User(Base):
        __tablename__ = "users"
        __table_args__ = {"extend_existing": True}

        id = Column(Integer, primary_key=True, index=True)
        username = Column(String, unique=True, index=True, nullable=False)
        email = Column(String, unique=True, index=True, nullable=False)
        hashed_password = Column(String, nullable=False)
        is_active = Column(Boolean, default=True)
        created_at = Column(DateTime(timezone=True), server_default=func.now())
except Exception as e:
    from sqlalchemy.exc import InvalidRequestError
    if isinstance(e, InvalidRequestError):
        pass
    else:
        raise
