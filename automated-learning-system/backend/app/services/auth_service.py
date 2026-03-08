"""Authentication service for user registration and login."""

from sqlalchemy.orm import Session
from app.models.user_model import User
from app.utils.security import hash_password, verify_password, create_access_token
from app.utils.logger import logger


def create_user(db: Session, email: str, password: str) -> User:
    """Register a new user with email and password."""
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        raise ValueError("Email already registered")
    user = User(email=email, hashed_password=hash_password(password))
    db.add(user)
    db.commit()
    db.refresh(user)
    logger.info(f"✓ User registered: {email}")
    return user


def authenticate_user(db: Session, email: str, password: str):
    """Authenticate user and return JWT token."""
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    token = create_access_token(str(user.id))
    logger.info(f"✓ User authenticated: {email}")
    return {"access_token": token, "token_type": "bearer", "user_id": user.id}

