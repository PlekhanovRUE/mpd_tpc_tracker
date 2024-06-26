import torch
import torch.nn as nn
from torch.nn.modules.loss import _Loss

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


class FCNeuralNet(nn.Module):
    def __init__(self):
        super(FCNeuralNet, self).__init__()
        self.layer1 = nn.Linear(8, 8)
        self.layer2 = nn.Linear(8, 10)
        self.layer3 = nn.Linear(10, 15)
        self.layer4 = nn.Linear(15, 10)
        self.output_layer = nn.Linear(10, 1)
        self.relu = nn.ReLU()
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        x = self.relu(self.layer1(x))
        x = self.relu(self.layer2(x))
        x = self.relu(self.layer3(x))
        x = self.relu(self.layer4(x))
        x = self.sigmoid(self.output_layer(x))
        return x
