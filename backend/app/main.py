from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.routing import Route, WebSocketRoute
from starlette.endpoints import WebSocketEndpoint
from starlette.requests import Request
from app.database import engine, Base, SessionLocal
from app.utils.logger import logger
from app.services import auth_service
from app.services.rl_engine import rl_engine
from app.models.emotion_log import EmotionLog
import json


async def health(request: Request):
    return JSONResponse({"status": "ok"})


async def register(request: Request):
    payload = await request.json()
    email = payload.get("email")
    password = payload.get("password")
    if not email or not password:
        return JSONResponse({"detail": "email and password required"}, status_code=400)
    db = SessionLocal()
    try:
        user = auth_service.register_user(db, email, password)
        return JSONResponse({"id": user.id, "email": user.email, "created_at": str(user.created_at)})
    except ValueError as e:
        return JSONResponse({"detail": str(e)}, status_code=400)
    finally:
        db.close()


async def login(request: Request):
    payload = await request.json()
    email = payload.get("email")
    password = payload.get("password")
    if not email or not password:
        return JSONResponse({"detail": "email and password required"}, status_code=400)
    db = SessionLocal()
    try:
        token = auth_service.authenticate_user(db, email, password)
        if not token:
            return JSONResponse({"detail": "Invalid credentials"}, status_code=401)
        return JSONResponse(token)
    finally:
        db.close()


async def analytics_summary(request: Request):
    db = SessionLocal()
    try:
        from sqlalchemy import func
        avg_emotion = db.query(func.avg(EmotionLog.emotion_score)).scalar() or 0.0
        avg_perf = db.query(func.avg(EmotionLog.performance_score)).scalar() or 0.0
        engagement = float((avg_perf * 0.6) + (avg_emotion * 0.4))
        return JSONResponse({"average_emotion": float(avg_emotion), "average_performance": float(avg_perf), "engagement_score": engagement})
    finally:
        db.close()


class EmotionWS(WebSocketEndpoint):
    encoding = "text"

    async def on_connect(self, websocket):
        await websocket.accept()

    async def on_receive(self, websocket, data):
        try:
            payload = json.loads(data)
        except Exception:
            await websocket.send_text(json.dumps({"error": "invalid_json"}))
            return

        facial = payload.get("facial_score")
        speech = payload.get("speech_score")
        typing = payload.get("typing_score")
        emotion_score = payload.get("emotion_score")
        performance_score = payload.get("performance_score")

        if emotion_score is None:
            # weighted fusion
            from app.multimodal.fusion import weighted_fusion
            fused = weighted_fusion(facial, speech, typing)
            emotion_score = float(fused)
        else:
            emotion_score = float(emotion_score)

        performance_score = float(performance_score) if performance_score is not None else 0.5

        action = rl_engine.get_adaptive_action(float(emotion_score), float(performance_score))

        db = SessionLocal()
        try:
            log = EmotionLog(user_id=None, emotion_score=float(emotion_score), performance_score=float(performance_score), adaptive_action=action)
            db.add(log)
            db.commit()
            db.refresh(log)
        finally:
            db.close()

        await websocket.send_text(json.dumps({"adaptive_action": action, "emotion_score": emotion_score, "performance_score": performance_score}))

    async def on_disconnect(self, websocket, close_code):
        return


middleware = [Middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"], allow_credentials=True)]

routes = [
    Route("/health", health, methods=["GET"]),
    Route("/auth/register", register, methods=["POST"]),
    Route("/auth/login", login, methods=["POST"]),
    Route("/analytics/summary", analytics_summary, methods=["GET"]),
    WebSocketRoute("/ws/emotion", EmotionWS),
]

app = Starlette(debug=False, routes=routes, middleware=middleware)


@app.on_event("startup")
async def startup_event():
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables ensured (Starlette server)")
    except Exception as e:
        # handle potential duplicate table/class registration during reloads
        from sqlalchemy.exc import InvalidRequestError
        if isinstance(e, InvalidRequestError):
            logger.warning(f"Ignored metadata registration error: {e}")
        else:
            logger.error(f"Unexpected error creating tables: {e}")
            raise
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
