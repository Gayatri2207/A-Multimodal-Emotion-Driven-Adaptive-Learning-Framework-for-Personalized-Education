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
