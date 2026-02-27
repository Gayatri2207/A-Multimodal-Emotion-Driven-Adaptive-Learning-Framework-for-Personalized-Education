import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F


class SimpleFacialCNN(nn.Module):
    def __init__(self, input_channels=1):
        super().__init__()
        self.conv1 = nn.Conv2d(input_channels, 16, kernel_size=3, padding=1)
        self.conv2 = nn.Conv2d(16, 32, kernel_size=3, padding=1)
        self.pool = nn.AdaptiveAvgPool2d((4, 4))
        self.fc = nn.Linear(32 * 4 * 4, 1)

    def forward(self, x):
        x = F.relu(self.conv1(x))
        x = F.relu(self.conv2(x))
        x = self.pool(x)
        x = x.view(x.size(0), -1)
        x = self.fc(x)
        return x


class FacialEmotionModel:
    def __init__(self, device: str = "cpu"):
        self.device = torch.device(device)
        self.model = SimpleFacialCNN().to(self.device)
        self.model.eval()

    def infer(self, image: np.ndarray) -> float:
        # image expected as grayscale numpy array normalized 0..1
        if image.ndim == 2:
            arr = image[np.newaxis, np.newaxis, :, :].astype(np.float32)
        elif image.ndim == 3 and image.shape[2] in (1, 3):
            arr = np.transpose(image, (2, 0, 1))[np.newaxis, ...].astype(np.float32)
            if arr.shape[1] == 3:
                arr = arr.mean(axis=1, keepdims=True)
        else:
            arr = np.zeros((1, 1, 48, 48), dtype=np.float32)
        tensor = torch.from_numpy(arr).to(self.device)
        with torch.no_grad():
            out = self.model(tensor)
            score = torch.sigmoid(out).item()
        return float(score)
import torch
import torch.nn as nn

class FacialEmotionCNN(nn.Module):
    def __init__(self, num_classes=7):
        super(FacialEmotionCNN, self).__init__()

        self.conv = nn.Sequential(
            nn.Conv2d(1, 32, 3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),

            nn.Conv2d(32, 64, 3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),

            nn.Conv2d(64, 128, 3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
        )

        self.fc = nn.Sequential(
            nn.Linear(128 * 6 * 6, 256),
            nn.ReLU(),
            nn.Linear(256, num_classes)
        )

    def forward(self, x):
        x = self.conv(x)
        x = x.view(x.size(0), -1)
        return self.fc(x)
