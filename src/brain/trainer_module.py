import json
import torch
import torch.nn as nn
import numpy as np
import random
from src.brain.nltk_utils import tokenize, stem, bag_of_words
from src.brain.model import NeuralNet
from src.config import INTENTS_PATH, MODEL_DATA_PATH

def run_training():
    # Set random seed for reproducibility
    random.seed(42)
    np.random.seed(42)
    torch.manual_seed(42)
    
    print("--- STARTING BRAIN TRAINING (High Precision) ---")
    
    # Loading training data
    with open(INTENTS_PATH, 'r') as f:
        intents = json.load(f)

    all_words = []
    tags = []
    xy = []
    
    # Processing intents and patterns
    for intent in intents['intents']:
        tag = intent['tag']
        tags.append(tag)
        for pattern in intent['patterns']:
            w = tokenize(pattern)
            all_words.extend(w)
            xy.append((w, tag))

    # Removing punctuation and stemming
    ignore_words = ['?', '!', '.', ',']
    all_words = [stem(w) for w in all_words if w not in ignore_words]
    all_words = sorted(set(all_words))
    tags = sorted(set(tags))

    # Preparing training data
    X_train = []
    y_train = []
    for (pattern_sentence, tag) in xy:
        bag = bag_of_words(pattern_sentence, all_words)
        X_train.append(bag)
        label = tags.index(tag)
        y_train.append(label)

    # Conversion to PyTorch tensors
    X_train = np.array(X_train)
    X_train = torch.tensor(X_train, dtype=torch.float32)
    y_train = torch.tensor(y_train, dtype=torch.long)

    # Network Hyperparameters (Increased precision)
    input_size = len(X_train[0])
    hidden_size = 16
    output_size = len(tags)
    learning_rate = 0.001
    num_epochs = 1200 

    # Device selection (GPU/CPU)
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
    model = NeuralNet(input_size, hidden_size, output_size).to(device)

    # Loss function and optimizer
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)

    # Training loop
    for epoch in range(num_epochs):
        outputs = model(X_train.to(device))
        loss = criterion(outputs, y_train.to(device))
        
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        
        if (epoch+1) % 100 == 0:
            print(f'Epoch [{epoch+1}/{num_epochs}], Loss: {loss.item():.6f}')

    # Saving the model
    data = {
        "model_state": model.state_dict(),
        "input_size": input_size,
        "hidden_size": hidden_size,
        "output_size": output_size,
        "all_words": all_words,
        "tags": tags
    }
    
    import os
    os.makedirs(os.path.dirname(MODEL_DATA_PATH), exist_ok=True)
    torch.save(data, MODEL_DATA_PATH)
    print(f"--- TRAINING COMPLETE | Final Loss: {loss.item():.6f} ---")
    return True
