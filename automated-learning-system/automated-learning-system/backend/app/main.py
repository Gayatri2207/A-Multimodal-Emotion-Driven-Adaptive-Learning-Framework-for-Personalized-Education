from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import auth_routes, emotion_routes, adaptive_routes, realtime_ws, analytics_routes
from app.database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Emotion Adaptive Learning API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_routes.router)
app.include_router(emotion_routes.router)
app.include_router(adaptive_routes.router)
app.include_router(realtime_ws.router)
app.include_router(analytics_routes.router)

@app.get("/")
def root():
    return {"message": "Emotion Adaptive Learning API Running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
