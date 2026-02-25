from fastapi import FastAPI
from app.routes import auth_routes, emotion_routes, adaptive_routes, realtime_ws
from app.database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Emotion Adaptive Learning API")

app.include_router(auth_routes.router)
app.include_router(emotion_routes.router)
app.include_router(adaptive_routes.router)
app.include_router(realtime_ws.router)

@app.get("/")
def home():
    return {"message": "Emotion Adaptive Learning System Running ??"}
