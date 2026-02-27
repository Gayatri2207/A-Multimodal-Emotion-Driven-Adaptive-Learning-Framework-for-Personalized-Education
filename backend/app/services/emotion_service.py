from sqlalchemy.orm import Session
from app.models.emotion_log import EmotionLog
from app.multimodal.facial_emotion.model import FacialEmotionModel
from app.multimodal.speech_emotion.model import SpeechEmotionModel
from app.multimodal.typing_behavior.analyzer import TypingBehaviorAnalyzer
from app.multimodal.fusion import weighted_fusion
from app.services.rl_engine import rl_engine
from app.utils.logger import logger
from typing import Optional


facial = FacialEmotionModel()
speech = SpeechEmotionModel()
typing_analyzer = TypingBehaviorAnalyzer()


def analyze_and_get_action(db: Session, user_id: Optional[int], image=None, audio=None, keystroke_intervals=None, mistakes=0, total_chars=0):
    facial_score = None
    speech_score = None
    typing_score = None
    try:
        if image is not None:
            facial_score = float(facial.infer(image))
    except Exception as e:
        logger.error(f"Facial inference error: {e}")
    try:
        if audio is not None:
            speech_score = float(speech.infer(audio))
    except Exception as e:
        logger.error(f"Speech inference error: {e}")
    try:
        if keystroke_intervals is not None:
            typing_score = float(typing_analyzer.analyze(keystroke_intervals, mistakes, total_chars))
    except Exception as e:
        logger.error(f"Typing analysis error: {e}")

    fused = weighted_fusion(facial_score, speech_score, typing_score)
    performance_estimate = typing_score if typing_score is not None else 0.5
    action = rl_engine.get_adaptive_action(fused, performance_estimate)

    log = EmotionLog(user_id=user_id, emotion_score=float(fused), performance_score=float(performance_estimate), adaptive_action=action)
    db.add(log)
    db.commit()
    db.refresh(log)
    return {"adaptive_action": action, "emotion_score": fused, "performance_score": performance_estimate}
def fuse_multimodal(facial, speech, typing):

    emotion_votes = {}

    for emotion in [facial, speech, typing]:
        emotion_votes[emotion] = emotion_votes.get(emotion, 0) + 1

    return max(emotion_votes, key=emotion_votes.get)
