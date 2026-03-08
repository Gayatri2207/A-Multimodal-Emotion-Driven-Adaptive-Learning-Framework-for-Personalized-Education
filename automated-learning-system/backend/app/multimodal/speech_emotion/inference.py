"""
Speech emotion inference wrapper.
Delegates to SpeechEmotionModel (Wav2Vec2 with heuristic fallback).
"""
from app.utils.logger import logger
from .model import predict_speech_emotion as _predict


def predict_speech_emotion(audio_path: str) -> float:
    """
    Load audio from file and predict emotion score.

    Args:
        audio_path: Path to a wav/mp3 audio file
    Returns:
        float in [0.0, 1.0]
    """
    try:
        import librosa
        audio, sr = librosa.load(audio_path, sr=16000)
        return _predict(audio, sampling_rate=sr)
    except Exception as e:
        logger.warning(f"Speech inference from file failed: {e}, returning neutral")
        return 0.5

