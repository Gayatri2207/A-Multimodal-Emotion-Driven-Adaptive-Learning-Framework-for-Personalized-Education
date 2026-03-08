"""
Train a speech emotion CNN on MFCC features.

Usage:
    python speech_emotion_training.py [--data-dir /path/to/features.npy] [--epochs 30]

Saves weights to ../backend/models/speech_emotion.pth
Note: For production use, prefer the Wav2Vec2 transformer in
      backend/app/multimodal/speech_emotion/model.py which doesn't need separate training.
"""

import argparse
import os
import sys
import torch
from torch import nn, optim
from torch.utils.data import DataLoader, TensorDataset

sys.path.append('../backend')


class SpeechEmotionCNN(nn.Module):
    """Simple 1-D CNN for MFCC feature sequences (40-dim, 4 emotion classes)."""
    def __init__(self, input_dim: int = 40, num_classes: int = 4):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, 128),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, num_classes),
        )

    def forward(self, x):
        return self.net(x)


def train(data_dir=None, epochs=30, batch_size=64, lr=1e-3, save_path="../backend/models/speech_emotion.pth"):
    os.makedirs(os.path.dirname(os.path.abspath(save_path)), exist_ok=True)
    num_classes = 4

    if data_dir:
        import numpy as np
        data = np.load(data_dir, allow_pickle=True).item()
        X = torch.tensor(data["X"], dtype=torch.float32)
        y = torch.tensor(data["y"], dtype=torch.long)
        print(f"Loaded data: {X.shape}")
    else:
        print("No data directory given — using synthetic MFCC data")
        X = torch.randn(400, 40)
        y = torch.randint(0, num_classes, (400,))

    dataset = TensorDataset(X, y)
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

    model = SpeechEmotionCNN(input_dim=X.shape[1], num_classes=num_classes)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=lr)

    for epoch in range(1, epochs + 1):
        model.train()
        total_loss, correct, total = 0.0, 0, 0
        for X_batch, y_batch in loader:
            optimizer.zero_grad()
            out = model(X_batch)
            loss = criterion(out, y_batch)
            loss.backward()
            optimizer.step()
            total_loss += loss.item() * len(y_batch)
            correct += (out.argmax(1) == y_batch).sum().item()
            total += len(y_batch)
        print(f"Epoch {epoch}/{epochs} — loss: {total_loss/total:.4f} — acc: {correct/total:.3f}")

    torch.save(model.state_dict(), save_path)
    print(f"✓ Speech emotion model saved to {save_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", default=None, help="Path to .npy file with X/y keys")
    parser.add_argument("--epochs", type=int, default=2)
    parser.add_argument("--save-path", default="../backend/models/speech_emotion.pth")
    args = parser.parse_args()
    train(data_dir=args.data_dir, epochs=args.epochs, save_path=args.save_path)

