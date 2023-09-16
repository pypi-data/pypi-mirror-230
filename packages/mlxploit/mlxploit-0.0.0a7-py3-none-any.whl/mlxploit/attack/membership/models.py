import torch.nn as nn
import torch.nn.functional as F


class ShadowNetCNN(nn.Module):
    """
    Shadow network - CNN

    This is suitable for MNIST dataset
    """
    def __init__(self, input_size: int = 1, hidden_size: int = 1, output_size: int =1):
        super(ShadowNetCNN, self).__init__()
        self.conv1 = nn.Conv2d(1, 32, kernel_size=3)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3)
        self.fc1 = nn.Linear(64 * 5 * 5, 128)
        self.fc2 = nn.Linear(128, output_size)

    def forward(self, x):
        x = F.relu(F.max_pool2d(self.conv1(x), 2))
        x = F.relu(F.max_pool2d(self.conv2(x), 2))
        x = x.view(-1, 64 * 5 * 5)
        x = F.relu(self.fc1(x))
        x = self.fc2(x)
        return x


class ShadowNetCNN2(nn.Module):
    """
    Shadow network - LeNet(CNN)

    This is suitable for CIFAR-10 dataset
    """
    def __init__(self, input_size: int = 1, hidden_size: int = 1, output_size: int = 1):
        # This is suitable for CIFAR-10 dataset
        super(ShadowNetCNN2, self).__init__()
        self.conv1 = nn.Conv2d(3, 6, kernel_size=5)
        self.pool = nn.MaxPool2d(2, 2)
        self.conv2 = nn.Conv2d(6, 16, kernel_size=5)
        self.fc1 = nn.Linear(16 * 5 * 5, 120)
        self.fc2 = nn.Linear(120, 84)
        self.fc3 = nn.Linear(84, output_size)

    def forward(self, x):
        x = self.pool(F.relu(self.conv1(x)))
        x = self.pool(F.relu(self.conv2(x)))
        x = x.view(-1, 16 * 5 * 5)
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = self.fc3(x)
        return x
    

class ShadowNetCNN3(nn.Module):
    """
    Shadow network - LeNet(CNN)
    """
    def __init__(self, input_size: int = 1, hidden_size: int = 1, output_size: int = 1):
        # This is optimized for CIFAR-10 dataset
        super(ShadowNetCNN3, self).__init__()
        self.conv1 = nn.Conv2d(3, 6, kernel_size=5)
        self.pool = nn.MaxPool2d(2, 2)
        self.conv2 = nn.Conv2d(6, 16, kernel_size=5)
        self.fc1 = nn.Linear(16 * 53 * 53, 120)  # 53 = math.sqrt(input_size=44944 / batch_size=1 / ouput_channels=16)
        self.fc2 = nn.Linear(120, 84)
        self.fc3 = nn.Linear(84, output_size)

    def forward(self, x):
        x = self.pool(F.relu(self.conv1(x)))
        x = self.pool(F.relu(self.conv2(x)))
        x = x.view(-1, 16 * 53 * 53)
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = self.fc3(x)
        return x
    

class AttackNet(nn.Module):
    """
    AttackNet used for attack model which classifies whether input data has been trained on target ML model.

    Arguments:
        input_size: The number of classes for predictions.
    """
    def __init__(self, input_size: int = 1):
        super(AttackNet, self).__init__()
        self.fc1 = nn.Linear(input_size, 32)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(32, 1)
        self.sigmoid = nn.Sigmoid()

    def forward(self, confidence_score):
        x = self.fc1(confidence_score)
        x = self.relu(x)
        x = self.fc2(x)
        x = self.sigmoid(x)
        return x
