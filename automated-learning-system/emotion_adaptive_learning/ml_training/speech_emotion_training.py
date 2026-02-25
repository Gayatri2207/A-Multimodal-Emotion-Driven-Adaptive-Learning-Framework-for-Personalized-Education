import torch
from torch import nn, optim
from torch.utils.data import DataLoader, TensorDataset
import sys
sys.path.append('../backend')
from app.multimodal.speech_emotion.model import SpeechEmotionCNN

def train_dummy():
    model = SpeechEmotionCNN()
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    criterion = nn.CrossEntropyLoss()

    dummy_x = torch.randn(100, 40)
    dummy_y = torch.randint(0, 4, (100,))

    dataset = TensorDataset(dummy_x, dummy_y)
    loader = DataLoader(dataset, batch_size=16)

    for epoch in range(2):
        for x, y in loader:
            optimizer.zero_grad()
            outputs = model(x)
            loss = criterion(outputs, y)
            loss.backward()
            optimizer.step()

    torch.save(model.state_dict(), "../data/models/speech_emotion.pth")
    print("Speech Emotion Model Trained & Saved")

if __name__ == "__main__":
    train_dummy()
