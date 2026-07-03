import torch
import torch.nn as nn

class NeuralNet(nn.Module):
    def __init__(self, input_size, hidden_size, num_classes):
        super(NeuralNet, self).__init__()
        # Pierwsza warstwa liniowa
        self.l1 = nn.Linear(input_size, hidden_size) 
        # Druga warstwa liniowa
        self.l2 = nn.Linear(hidden_size, hidden_size) 
        # Warstwa wyjściowa
        self.l3 = nn.Linear(hidden_size, num_classes)
        # Funkcja aktywacji ReLU
        self.relu = nn.ReLU()
    
    def forward(self, x):
        out = self.l1(x)
        out = self.relu(out)
        out = self.l2(out)
        out = self.relu(out)
        out = self.l3(out)
        # Softmax nie jest tutaj potrzebny, jest stosowany automatycznie w CrossEntropyLoss
        return out
