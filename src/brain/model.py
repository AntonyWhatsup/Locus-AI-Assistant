import torch
import torch.nn as nn

class NeuralNet(nn.Module):
    def __init__(self, input_size, hidden_size, num_classes):
        super(NeuralNet, self).__init__()
        # First linear layer
        self.l1 = nn.Linear(input_size, hidden_size) 
        # Second linear layer
        self.l2 = nn.Linear(hidden_size, hidden_size) 
        # Output layer
        self.l3 = nn.Linear(hidden_size, num_classes)
        # ReLU activation function
        self.relu = nn.ReLU()
    
    def forward(self, x):
        out = self.l1(x)
        out = self.relu(out)
        out = self.l2(out)
        out = self.relu(out)
        out = self.l3(out)
        # Softmax is not needed here, it is automatically applied in CrossEntropyLoss
        return out
