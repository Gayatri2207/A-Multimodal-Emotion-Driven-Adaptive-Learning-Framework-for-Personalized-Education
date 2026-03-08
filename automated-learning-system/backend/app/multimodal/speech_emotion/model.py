"""
Speech emotion model.
Attempts to load a pre-trained Wav2Vec2 transformer for speech emotion recognition;
falls back to a lightweight heuristic if the model is unavailable.
"""

import os
import random
from app.utils.logger import logger

try:
    import numpy as np
    HAS_NUMPY = True
except Exception:
    HAS_NUMPY = False

try:
    import torch
    from transformers import Wav2Vec2Processor, Wav2Vec2ForSequenceClassification
    HAS_TRANSFORMERS = True
except Exception:
    HAS_TRANSFORMERS = False

# Map transformer emotion labels → valence score [0, 1]
_LABEL_VALENCE = {
    "neu": 0.5,
    "hap": 1.0,
    "ang": 0.05,
    "sad": 0.1,
    "fea": 0.15,
    "dis": 0.1,
    "sur": 0.75,
    "calm": 0.6,
    "neutral": 0.5,
    "happy": 1.0,
    "angry": 0.05,
    "fearful": 0.15,
    "disgust": 0.1,
    "surprised": 0.75,
}
_HF_MODEL_NAME = "superb/wav2vec2-base-superb-er"


class SpeechEmotionModel:
    """
    Wraps a Wav2Vec2-based speech emotion classifier.
    Loads lazily on first inference call to avoid blocking server startup.
    Falls back to heuristic if Transformers is unavailable.
    """

    def __init__(self):
        self._processor = None
        self._model = None
        self._ready = False
        self._attempted = False

    def _lazy_load(self):
        """Load the transformer model on first use."""
        if self._attempted:
            return
        self._attempted = True
        if not HAS_TRANSFORMERS:
            logger.warning("Transformers not available — speech model using heuristic fallback")
            return
        try:
            logger.info(f"Loading speech emotion model: {_HF_MODEL_NAME} …")
            self._processor = Wav2Vec2Processor.from_pretrained(_HF_MODEL_NAME)
            self._model = Wav2Vec2ForSequenceClassification.from_pretrained(_HF_MODEL_NAME)
            self._model.eval()
            self._ready = True
            logger.info("✓ Speech emotion model loaded (Wav2Vec2)")
        except Exception as e:
            logger.warning(f"Speech model load failed: {e} — using heuristic fallback")

    def predict(self, audio_data, sampling_rate: int = 16000) -> float:
        """
        Predict positive-valence emotion score in [0, 1].

        Args:
            audio_data: 1-D numpy float32 array of audio samples, or None
            sampling_rate: sample rate in Hz (default 16000)
        Returns:
            float in [0.0, 1.0]
        """
        if audio_data is None:
            return 0.5
        self._lazy_load()
        if self._ready:
            return self._transformer_predict(audio_data, sampling_rate)
        return self._heuristic(audio_data)

    def _transformer_predict(self, audio_data, sampling_rate: int) -> float:
        try:
            import numpy as np
            arr = np.array(audio_data, dtype=np.float32)
            inputs = self._processor(arr, sampling_rate=sampling_rate, return_tensors="pt", padding=True)
            with torch.no_grad():
                logits = self._model(**inputs).logits
            predicted_idx = int(torch.argmax(logits, dim=-1).item())
            label = self._model.config.id2label.get(predicted_idx, "neutral")
            score = _LABEL_VALENCE.get(label.lower(), 0.5)
            return float(max(0.0, min(1.0, score)))
        except Exception as e:
            logger.debug(f"Transformer speech predict failed: {e}, using heuristic")
            return self._heuristic(audio_data)

    @staticmethod
    def _heuristic(audio_data) -> float:
        """Deterministic fallback based on RMS energy."""
        try:
            import numpy as np
            arr = np.array(audio_data, dtype=np.float32)
            rms = float(np.sqrt(np.mean(arr ** 2)))
            # Map RMS [0, 0.5] → [0.3, 0.7]
            score = 0.3 + min(1.0, rms / 0.5) * 0.4
            return round(score, 3)
        except Exception:
            return 0.5


# Module-level singleton
speech_emotion_model = SpeechEmotionModel()


def predict_speech_emotion(audio_data=None, sampling_rate: int = 16000) -> float:
    """Convenience wrapper."""
    return speech_emotion_model.predict(audio_data, sampling_rate)

