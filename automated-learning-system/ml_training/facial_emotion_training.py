"""
Train a FacialEmotionCNN on FER2013-style data.

Usage:
    python facial_emotion_training.py [--data-dir /path/to/fer2013] [--epochs 30]

If no data directory is given, synthetic data is used for a quick smoke-test.
Saves weights to ../backend/models/facial_emotion.pth
"""

import argparse
import os
import sys
import torch
from torch import nn, optim
from torch.utils.data import DataLoader, TensorDataset

sys.path.append('../backend')
from app.multimodal.facial_emotion.model import FacialEmotionCNN


def load_fer_data(data_dir: str):
    """Load FER2013 images from a directory structured as class sub-folders."""
    from torchvision import datasets, transforms
    transform = transforms.Compose([
        transforms.Grayscale(),
        transforms.Resize((48, 48)),
        transforms.RandomHorizontalFlip(),
        transforms.ToTensor(),
        transforms.Normalize([0.5], [0.5]),
    ])
    return datasets.ImageFolder(data_dir, transform=transform)


def train(data_dir=None, epochs=30, batch_size=64, lr=1e-3, save_path="../backend/models/facial_emotion.pth"):
    os.makedirs(os.path.dirname(os.path.abspath(save_path)), exist_ok=True)
    num_classes = 7

    if data_dir:
        print(f"Loading FER2013 data from {data_dir}")
        dataset = load_fer_data(data_dir)
    else:
        print("No data directory given — using synthetic data for smoke-test")
        dummy_x = torch.randn(200, 1, 48, 48)
        dummy_y = torch.randint(0, num_classes, (200,))
        dataset = TensorDataset(dummy_x, dummy_y)

    loader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
    model = FacialEmotionCNN(num_classes=num_classes)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=lr)
    scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=10, gamma=0.5)

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
        scheduler.step()
        print(f"Epoch {epoch}/{epochs} — loss: {total_loss/total:.4f} — acc: {correct/total:.3f}")

    torch.save(model.state_dict(), save_path)
    print(f"✓ Facial emotion model saved to {save_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", default=None, help="Path to FER2013 ImageFolder structure")
    parser.add_argument("--epochs", type=int, default=2, help="Training epochs (default 2 for smoke-test)")
    parser.add_argument("--save-path", default="../backend/models/facial_emotion.pth")
    args = parser.parse_args()
    train(data_dir=args.data_dir, epochs=args.epochs, save_path=args.save_path)

