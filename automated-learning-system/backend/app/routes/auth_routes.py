from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr

from app.database import get_db
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

@router.post("/register")
async def register(user: UserCreate, db: Session = Depends(get_db)):
    try:
        u = auth_service.create_user(db, user.email, user.password)
        # Auto-login: return token so the client is immediately authenticated
        token_data = auth_service.authenticate_user(db, user.email, user.password)
        return token_data
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/login")
async def login(user: UserLogin, db: Session = Depends(get_db)):
    token = auth_service.authenticate_user(db, user.email, user.password)
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return token
