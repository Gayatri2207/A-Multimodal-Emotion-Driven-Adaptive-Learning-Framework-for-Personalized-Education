import numpy as np
from typing import Optional
import torch
from transformers import Wav2Vec2ForSequenceClassification, Wav2Vec2Processor
from app.config import settings
from app.utils.logger import logger


class SpeechEmotionModel:
    def __init__(self, model_name: Optional[str] = None, device: str = "cpu"):
        self.model_name = model_name or settings.WAV2VEC_MODEL
        self.device = device
        self.model = None
        self.processor = None
        try:
            self.processor = Wav2Vec2Processor.from_pretrained(self.model_name)
            self.model = Wav2Vec2ForSequenceClassification.from_pretrained(self.model_name)
            self.model.to(self.device)
        except Exception as e:
            logger.error(f"Speech model init failed: {e}")
            self.model = None

    def infer(self, audio: np.ndarray, sampling_rate: int = 16000) -> float:
        if self.model is None or self.processor is None:
            # graceful fallback
            return 0.5
        try:
            inputs = self.processor(audio, sampling_rate=sampling_rate, return_tensors="pt", padding=True)
            with torch.no_grad():
                logits = self.model(**inputs).logits
            probs = logits.softmax(dim=-1).cpu().numpy()
            # map to score 0..1 using argmax class index
            score = float(np.max(probs))
            return score
        except Exception as e:
            logger.error(f"Speech infer failed: {e}")
            return 0.5
import torch
import torch.nn as nn

class SpeechEmotionCNN(nn.Module):
    def __init__(self, input_size=40, num_classes=4):
        super(SpeechEmotionCNN, self).__init__()

        self.fc = nn.Sequential(
            nn.Linear(input_size, 128),
            nn.ReLU(),
            nn.Linear(128, num_classes)
        )

    def forward(self, x):
        return self.fc(x)
