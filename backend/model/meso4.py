import torch
import torch.nn as nn
import torch.nn.functional as F


class Meso4(nn.Module):
    def __init__(self, num_classes=2):
        super(Meso4, self).__init__()
        self.conv1 = nn.Conv2d(3, 8, kernel_size=3, padding=1)
        self.conv2 = nn.Conv2d(8, 8, kernel_size=5, padding=2)
        self.conv3 = nn.Conv2d(8, 16, kernel_size=5, padding=2)
        self.conv4 = nn.Conv2d(16, 16, kernel_size=5, padding=2)

        self.batchnorm1 = nn.BatchNorm2d(8)
        self.batchnorm2 = nn.BatchNorm2d(8)
        self.batchnorm3 = nn.BatchNorm2d(16)
        self.batchnorm4 = nn.BatchNorm2d(16)

        self.pool = nn.MaxPool2d(2, stride=2, padding=0)
        self.global_pool = nn.AdaptiveAvgPool2d((1, 1))

        self.fc1 = nn.Linear(16, 16)
        self.fc2 = nn.Linear(16, num_classes)

        self.dropout = nn.Dropout(0.5)
        self.leakyrelu = nn.LeakyReLU(negative_slope=0.1)

    def forward(self, x):
        x = self.pool(F.relu(self.batchnorm1(self.conv1(x))))
        x = self.pool(F.relu(self.batchnorm2(self.conv2(x))))
        x = self.pool(F.relu(self.batchnorm3(self.conv3(x))))
        x = self.pool(F.relu(self.batchnorm4(self.conv4(x))))

        x = self.global_pool(x)
        x = torch.flatten(x, 1)

        x = self.dropout(self.leakyrelu(self.fc1(x)))
        x = self.dropout(self.fc2(x))
        return x
