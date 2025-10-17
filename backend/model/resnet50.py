from torchvision import models
import torch.nn as nn

resnet50 = models.resnet50(pretrained=True)
resnet50.fc = nn.Sequential(
    nn.Linear(resnet50.fc.in_features, 512),
    nn.ReLU(),
    nn.Dropout(0.5),
    nn.Linear(512, 2),  # 2 nhãn fake và real
)
