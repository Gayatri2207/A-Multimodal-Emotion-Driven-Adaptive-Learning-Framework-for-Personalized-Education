"""
Dataset Download Script
=======================
Downloads free emotion datasets for training the emotion detection model.

Datasets supported:
  1. FER2013     — 35k facial images, 7 emotions (Kaggle)
  2. RAF-DB      — 30k real-world facial images (Kaggle)
  3. RAVDESS     — Speech emotion audio clips (Zenodo)
  4. Keystroke   — Typing dynamics dataset (Kaggle)

Usage:
  # Download all (requires kaggle API token at ~/.kaggle/kaggle.json)
  python scripts/download_datasets.py --all

  # Download specific dataset
  python scripts/download_datasets.py --fer2013
  python scripts/download_datasets.py --ravdess
  python scripts/download_datasets.py --rafdb

  # Skip Kaggle (download only public datasets)
  python scripts/download_datasets.py --ravdess --no-kaggle

Kaggle API setup:
  1. Go to https://www.kaggle.com → Account → Create API Token
  2. Save the downloaded kaggle.json to C:\\Users\\<you>\\.kaggle\\kaggle.json
  3. pip install kaggle
"""

import argparse
import os
import sys
import zipfile
from pathlib import Path

BASE_DIR   = Path(__file__).parent.parent
DATA_DIR   = BASE_DIR / "data"
EMOTION_DIR = DATA_DIR / "emotion_datasets"
SPEECH_DIR  = DATA_DIR / "speech_datasets"
TYPING_DIR  = DATA_DIR / "typing_datasets"
MODELS_DIR  = BASE_DIR / "models"

# Ensure directories exist
for d in [EMOTION_DIR, SPEECH_DIR, TYPING_DIR, MODELS_DIR]:
    d.mkdir(parents=True, exist_ok=True)


def _check_kaggle():
    """Return True if kaggle CLI is available and authenticated."""
    try:
        import kaggle  # noqa: F401
        return True
    except ImportError:
        print("  ⚠  kaggle package not installed. Run: pip install kaggle")
        return False
    except Exception as e:
        print(f"  ⚠  kaggle not configured: {e}")
        print("     Set up ~/.kaggle/kaggle.json — see: https://github.com/Kaggle/kaggle-api")
        return False


def download_fer2013():
    """Download FER2013 from Kaggle (msambare/fer2013)."""
    dest = EMOTION_DIR / "fer2013"
    if (dest / "train").exists():
        print(f"  ✓ FER2013 already downloaded at {dest}")
        return True

    print("📥 Downloading FER2013 (35k facial emotion images)...")
    if not _check_kaggle():
        print("  ℹ  Manual download: https://www.kaggle.com/datasets/msambare/fer2013")
        print(f"     Extract to: {dest}")
        return False

    import kaggle
    dest.mkdir(parents=True, exist_ok=True)
    try:
        kaggle.api.dataset_download_files(
            "msambare/fer2013",
            path=str(dest),
            unzip=True,
            quiet=False,
        )
        print(f"  ✓ FER2013 downloaded to {dest}")
        return True
    except Exception as e:
        print(f"  ✗ FER2013 download failed: {e}")
        return False


def download_rafdb():
    """Download RAF-DB from Kaggle (shuvoalok/raf-db-dataset)."""
    dest = EMOTION_DIR / "raf_db"
    if dest.exists() and any(dest.iterdir()):
        print(f"  ✓ RAF-DB already downloaded at {dest}")
        return True

    print("📥 Downloading RAF-DB (30k real-world facial expressions)...")
    if not _check_kaggle():
        print("  ℹ  Manual download: https://www.kaggle.com/datasets/shuvoalok/raf-db-dataset")
        print(f"     Extract to: {dest}")
        return False

    import kaggle
    dest.mkdir(parents=True, exist_ok=True)
    try:
        kaggle.api.dataset_download_files(
            "shuvoalok/raf-db-dataset",
            path=str(dest),
            unzip=True,
            quiet=False,
        )
        print(f"  ✓ RAF-DB downloaded to {dest}")
        return True
    except Exception as e:
        print(f"  ✗ RAF-DB download failed: {e}")
        return False


def download_ravdess():
    """Download RAVDESS speech emotion dataset from Zenodo (no auth required)."""
    dest = SPEECH_DIR / "ravdess"
    audio_files = list(dest.glob("**/*.wav")) if dest.exists() else []
    if len(audio_files) > 100:
        print(f"  ✓ RAVDESS already downloaded ({len(audio_files)} wav files)")
        return True

    print("📥 Downloading RAVDESS speech emotion dataset (Zenodo, ~1.2 GB)...")
    dest.mkdir(parents=True, exist_ok=True)

    try:
        import requests
        # Zenodo record for RAVDESS
        zenodo_url = "https://zenodo.org/record/1188976/files/Audio_Speech_Actors_01-24.zip"
        zip_path = dest / "ravdess.zip"

        print(f"  Downloading from {zenodo_url} ...")
        with requests.get(zenodo_url, stream=True, timeout=60) as r:
            r.raise_for_status()
            total = int(r.headers.get("content-length", 0))
            downloaded = 0
            with open(zip_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total:
                        pct = downloaded / total * 100
                        print(f"\r  {pct:.1f}% ({downloaded/1e6:.1f} MB / {total/1e6:.1f} MB)", end="", flush=True)
        print()

        print("  Extracting...")
        with zipfile.ZipFile(zip_path, "r") as z:
            z.extractall(dest)
        zip_path.unlink()
        print(f"  ✓ RAVDESS downloaded to {dest}")
        return True
    except Exception as e:
        print(f"  ✗ RAVDESS download failed: {e}")
        print("  ℹ  Manual download: https://zenodo.org/record/1188976")
        print(f"     Extract to: {dest}")
        return False


def download_keystroke():
    """Download Keystroke Dynamics dataset from Kaggle."""
    dest = TYPING_DIR / "keystroke"
    if dest.exists() and any(dest.glob("*.csv")):
        print(f"  ✓ Keystroke dataset already downloaded at {dest}")
        return True

    print("📥 Downloading Keystroke Dynamics dataset...")
    if not _check_kaggle():
        print("  ℹ  Manual download: https://www.kaggle.com/datasets/rtatman/keystroke-dynamics")
        print(f"     Extract to: {dest}")
        return False

    import kaggle
    dest.mkdir(parents=True, exist_ok=True)
    try:
        kaggle.api.dataset_download_files(
            "rtatman/keystroke-dynamics",
            path=str(dest),
            unzip=True,
            quiet=False,
        )
        print(f"  ✓ Keystroke dataset downloaded to {dest}")
        return True
    except Exception as e:
        print(f"  ✗ Keystroke download failed: {e}")
        return False


def download_hf_emotion_model():
    """Pre-download the HuggingFace ViT emotion model for offline use."""
    print("📥 Pre-downloading HuggingFace ViT emotion model (trpakov/vit-face-expression)...")
    try:
        from transformers import pipeline
        pipe = pipeline(
            "image-classification",
            model="trpakov/vit-face-expression",
            device=-1,
        )
        print("  ✓ HuggingFace ViT model cached")
        return True
    except Exception as e:
        print(f"  ⚠  HuggingFace model pre-download failed: {e}")
        print("     It will be downloaded automatically on first inference.")
        return False


def print_summary(results: dict):
    print("\n" + "=" * 50)
    print("Download Summary")
    print("=" * 50)
    for name, ok in results.items():
        icon = "✅" if ok else "❌"
        print(f"  {icon} {name}")

    failed = [k for k, v in results.items() if not v]
    if failed:
        print(f"\n⚠  {len(failed)} dataset(s) need manual download:")
        print("   FER2013 → https://www.kaggle.com/datasets/msambare/fer2013")
        print("   RAF-DB  → https://www.kaggle.com/datasets/shuvoalok/raf-db-dataset")
        print("   RAVDESS → https://zenodo.org/record/1188976")
        print("   Keystroke → https://www.kaggle.com/datasets/rtatman/keystroke-dynamics")
        print("\n   For Kaggle: pip install kaggle && set up ~/.kaggle/kaggle.json")


def main():
    parser = argparse.ArgumentParser(description="Download emotion datasets")
    parser.add_argument("--all",       action="store_true", help="Download all datasets")
    parser.add_argument("--fer2013",   action="store_true", help="FER2013 facial dataset")
    parser.add_argument("--rafdb",     action="store_true", help="RAF-DB facial dataset")
    parser.add_argument("--ravdess",   action="store_true", help="RAVDESS speech dataset")
    parser.add_argument("--keystroke", action="store_true", help="Keystroke dynamics dataset")
    parser.add_argument("--hf-model",  action="store_true", help="Pre-download HuggingFace ViT model")
    args = parser.parse_args()

    if not any(vars(args).values()):
        parser.print_help()
        print("\nRun with --all to download everything, or specify individual datasets.")
        sys.exit(0)

    results = {}

    if args.all or args.fer2013:
        results["FER2013"] = download_fer2013()
    if args.all or args.rafdb:
        results["RAF-DB"] = download_rafdb()
    if args.all or args.ravdess:
        results["RAVDESS"] = download_ravdess()
    if args.all or args.keystroke:
        results["Keystroke"] = download_keystroke()
    if args.all or args.hf_model:
        results["HuggingFace ViT"] = download_hf_emotion_model()

    print_summary(results)


if __name__ == "__main__":
    main()
