import torch
import librosa
from transformers import Wav2Vec2Processor, Wav2Vec2ForSequenceClassification

processor = Wav2Vec2Processor.from_pretrained("superb/wav2vec2-base-superb-er")
model = Wav2Vec2ForSequenceClassification.from_pretrained("superb/wav2vec2-base-superb-er")

def predict_speech_emotion(audio_path):

    speech, sr = librosa.load(audio_path, sr=16000)

    inputs = processor(speech, sampling_rate=16000, return_tensors="pt", padding=True)

    with torch.no_grad():
        logits = model(**inputs).logits

    predicted = torch.argmax(logits, dim=-1).item()

    labels = model.config.id2label

    return labels[predicted]
