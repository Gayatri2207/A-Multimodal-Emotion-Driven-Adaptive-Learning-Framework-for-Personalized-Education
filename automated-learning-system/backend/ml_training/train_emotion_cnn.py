"""
Emotion CNN Training Script
============================
Trains a lightweight ResNet18-based CNN on FER2013 (or RAF-DB) for 7-class
facial emotion recognition.  Saved weights are loaded automatically by the
backend (FACIAL_MODEL_PATH in .env).

Prerequisites:
  pip install torch torchvision tqdm

Dataset structure expected (after running download_datasets.py):
  data/emotion_datasets/fer2013/
    train/
      angry/  disgust/  fear/  happy/  neutral/  sad/  surprise/
    test/
      angry/  ...

  OR for RAF-DB:
  data/emotion_datasets/raf_db/
    train/  test/   (same sub-folder structure)

Usage:
  # Train on FER2013 (default)
  python ml_training/train_emotion_cnn.py

  # Train on RAF-DB
  python ml_training/train_emotion_cnn.py --dataset raf_db

  # Custom epochs and batch size
  python ml_training/train_emotion_cnn.py --epochs 30 --batch-size 64

  # Resume from checkpoint
  python ml_training/train_emotion_cnn.py --resume models/emotion_checkpoint.pth

Output:
  models/facial_emotion.pth   — best validation accuracy weights
  models/emotion_checkpoint.pth — latest checkpoint for resuming
"""

import argparse
import os
import sys
import time
from pathlib import Path

BASE_DIR   = Path(__file__).parent.parent
DATA_DIR   = BASE_DIR / "data" / "emotion_datasets"
MODELS_DIR = BASE_DIR / "models"
MODELS_DIR.mkdir(parents=True, exist_ok=True)

# FER2013 emotion classes (alphabetical = torchvision ImageFolder order)
EMOTION_CLASSES = ["angry", "disgust", "fear", "happy", "neutral", "sad", "surprise"]

# Valence weights per class (0=negative, 1=positive)
VALENCE = {
    "angry":    0.0,
    "disgust":  0.1,
    "fear":     0.15,
    "happy":    1.0,
    "neutral":  0.5,
    "sad":      0.1,
    "surprise": 0.75,
}


def check_dependencies():
    missing = []
    try:
        import torch  # noqa: F401
        import torchvision  # noqa: F401
    except ImportError:
        missing.append("torch torchvision")
    try:
        from tqdm import tqdm  # noqa: F401
    except ImportError:
        missing.append("tqdm")
    if missing:
        print(f"Missing dependencies: {' '.join(missing)}")
        print(f"Install with: pip install {' '.join(missing)}")
        sys.exit(1)


def build_model(num_classes: int = 7, pretrained: bool = True):
    """ResNet18 with modified first conv (handles grayscale) and custom head."""
    import torch.nn as nn
    import torchvision.models as models

    model = models.resnet18(weights="DEFAULT" if pretrained else None)

    # Replace first conv to accept 1-channel (grayscale) input
    model.conv1 = nn.Conv2d(1, 64, kernel_size=7, stride=2, padding=3, bias=False)

    # Replace final FC layer
    model.fc = nn.Sequential(
        nn.Dropout(0.4),
        nn.Linear(model.fc.in_features, num_classes),
    )
    return model


def get_transforms(image_size: int = 48):
    """Return train and val transforms."""
    import torchvision.transforms as T

    train_tf = T.Compose([
        T.Resize((image_size, image_size)),
        T.Grayscale(num_output_channels=1),
        T.RandomHorizontalFlip(),
        T.RandomRotation(10),
        T.ColorJitter(brightness=0.2, contrast=0.2),
        T.ToTensor(),
        T.Normalize(mean=[0.5], std=[0.5]),
    ])

    val_tf = T.Compose([
        T.Resize((image_size, image_size)),
        T.Grayscale(num_output_channels=1),
        T.ToTensor(),
        T.Normalize(mean=[0.5], std=[0.5]),
    ])

    return train_tf, val_tf


def train(args):
    import torch
    import torch.nn as nn
    import torch.optim as optim
    from torch.utils.data import DataLoader
    import torchvision.datasets as datasets
    from tqdm import tqdm

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"🖥  Device: {device}")

    dataset_path = DATA_DIR / args.dataset
    train_dir = dataset_path / "train"
    val_dir   = dataset_path / "test"

    if not train_dir.exists():
        print(f"✗ Training data not found at {train_dir}")
        print("  Run first: python scripts/download_datasets.py --fer2013")
        sys.exit(1)

    train_tf, val_tf = get_transforms(args.image_size)

    train_ds = datasets.ImageFolder(str(train_dir), transform=train_tf)
    val_ds   = datasets.ImageFolder(str(val_dir),   transform=val_tf) if val_dir.exists() else None

    train_loader = DataLoader(train_ds, batch_size=args.batch_size, shuffle=True,
                              num_workers=args.workers, pin_memory=True)
    val_loader = (DataLoader(val_ds, batch_size=args.batch_size, shuffle=False,
                             num_workers=args.workers, pin_memory=True)
                  if val_ds else None)

    print(f"📂 Dataset:    {args.dataset}")
    print(f"   Classes:    {train_ds.classes}")
    print(f"   Train size: {len(train_ds)}")
    print(f"   Val size:   {len(val_ds) if val_ds else 'N/A'}")

    model = build_model(num_classes=len(train_ds.classes), pretrained=args.pretrained)
    model = model.to(device)

    if args.resume and Path(args.resume).exists():
        ckpt = torch.load(args.resume, map_location=device)
        model.load_state_dict(ckpt["model_state"])
        print(f"  Resumed from {args.resume} (epoch {ckpt.get('epoch', '?')})")

    # Class-weighted loss to handle FER2013 imbalance
    class_counts = [len(list((train_dir / cls).glob("*")))
                    for cls in train_ds.classes
                    if (train_dir / cls).exists()]
    if class_counts and len(class_counts) == len(train_ds.classes):
        total = sum(class_counts)
        weights = torch.tensor([total / (c * len(class_counts)) for c in class_counts],
                                dtype=torch.float32).to(device)
        criterion = nn.CrossEntropyLoss(weight=weights)
        print(f"   Class weights: {[f'{w:.2f}' for w in weights.tolist()]}")
    else:
        criterion = nn.CrossEntropyLoss()

    optimizer = optim.AdamW(model.parameters(), lr=args.lr, weight_decay=1e-4)
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=args.epochs)

    best_val_acc = 0.0
    best_path    = MODELS_DIR / "facial_emotion.pth"
    ckpt_path    = MODELS_DIR / "emotion_checkpoint.pth"

    for epoch in range(1, args.epochs + 1):
        # ── Training ──────────────────────────────────────────────────────────
        model.train()
        train_loss, train_correct, train_total = 0.0, 0, 0
        t0 = time.time()

        with tqdm(train_loader, desc=f"Epoch {epoch:02d}/{args.epochs} [train]",
                  leave=False, unit="batch") as pbar:
            for images, labels in pbar:
                images, labels = images.to(device), labels.to(device)
                optimizer.zero_grad()
                outputs = model(images)
                loss = criterion(outputs, labels)
                loss.backward()
                optimizer.step()

                train_loss    += loss.item() * images.size(0)
                preds          = outputs.argmax(dim=1)
                train_correct += (preds == labels).sum().item()
                train_total   += images.size(0)
                pbar.set_postfix(loss=f"{loss.item():.4f}")

        train_acc  = train_correct / train_total * 100
        train_loss /= train_total

        # ── Validation ────────────────────────────────────────────────────────
        val_acc  = 0.0
        val_loss = 0.0
        if val_loader:
            model.eval()
            val_correct, val_total = 0, 0
            with torch.no_grad():
                for images, labels in val_loader:
                    images, labels = images.to(device), labels.to(device)
                    outputs = model(images)
                    loss    = criterion(outputs, labels)
                    val_loss += loss.item() * images.size(0)
                    preds    = outputs.argmax(dim=1)
                    val_correct += (preds == labels).sum().item()
                    val_total   += images.size(0)
            val_acc  = val_correct / val_total * 100
            val_loss /= val_total

        scheduler.step()
        elapsed = time.time() - t0

        # ── Logging ───────────────────────────────────────────────────────────
        val_str = f"  val_loss={val_loss:.4f}  val_acc={val_acc:.1f}%" if val_loader else ""
        print(f"Epoch {epoch:02d}/{args.epochs}  "
              f"train_loss={train_loss:.4f}  train_acc={train_acc:.1f}%"
              f"{val_str}  [{elapsed:.0f}s]")

        # Save checkpoint every epoch
        torch.save({
            "epoch":       epoch,
            "model_state": model.state_dict(),
            "optimizer":   optimizer.state_dict(),
            "val_acc":     val_acc,
        }, ckpt_path)

        # Save best model
        compare_acc = val_acc if val_loader else train_acc
        if compare_acc > best_val_acc:
            best_val_acc = compare_acc
            torch.save(model.state_dict(), best_path)
            print(f"  💾 New best model saved → {best_path}  (acc={best_val_acc:.1f}%)")

    print(f"\n✅ Training complete. Best accuracy: {best_val_acc:.1f}%")
    print(f"   Weights saved to: {best_path}")
    print(f"   Set FACIAL_MODEL_PATH={best_path} in backend/.env to use this model.")


def main():
    check_dependencies()

    parser = argparse.ArgumentParser(description="Train emotion CNN")
    parser.add_argument("--dataset",    default="fer2013",
                        help="Dataset folder name under data/emotion_datasets/ (default: fer2013)")
    parser.add_argument("--epochs",     type=int, default=25,
                        help="Number of training epochs (default: 25)")
    parser.add_argument("--batch-size", type=int, default=64,
                        help="Batch size (default: 64)")
    parser.add_argument("--lr",         type=float, default=1e-3,
                        help="Learning rate (default: 0.001)")
    parser.add_argument("--image-size", type=int, default=48,
                        help="Input image size in pixels (default: 48)")
    parser.add_argument("--workers",    type=int, default=2,
                        help="DataLoader worker threads (default: 2)")
    parser.add_argument("--no-pretrained", dest="pretrained", action="store_false",
                        help="Train from scratch (no ImageNet pretrained weights)")
    parser.add_argument("--resume",     default=None,
                        help="Path to checkpoint to resume from")
    parser.set_defaults(pretrained=True)
    args = parser.parse_args()

    train(args)


if __name__ == "__main__":
    main()
