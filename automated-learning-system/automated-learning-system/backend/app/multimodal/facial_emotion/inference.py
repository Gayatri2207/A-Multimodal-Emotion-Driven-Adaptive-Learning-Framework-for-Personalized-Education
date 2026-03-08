import torch
import cv2
import numpy as np
from .model import FacialEmotionCNN
from app.utils.helpers import map_emotion_label

model = FacialEmotionCNN()
model.eval()

def predict_frame(frame):

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    face = cv2.resize(gray, (48, 48))
    face = face / 255.0

    tensor = torch.tensor(face, dtype=torch.float32).unsqueeze(0).unsqueeze(0)

    with torch.no_grad():
        output = model(tensor)
        _, predicted = torch.max(output, 1)

    return map_emotion_label(predicted.item())


def live_webcam_emotion():
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        emotion = predict_frame(frame)

        cv2.putText(frame, emotion, (50, 50),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1, (0, 255, 0), 2)

        cv2.imshow("Emotion Detection", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
