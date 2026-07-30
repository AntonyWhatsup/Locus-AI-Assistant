import json
import os
import random

import numpy as np
import torch
import torch.nn as nn

from src.brain.model import NeuralNet
from src.brain.nltk_utils import bag_of_words, stem, tokenize
from src.config import INTENTS_PATH, MODEL_DATA_PATH


IGNORE_WORDS = {"?", "!", ".", ","}
TRAINING_RANDOM_SEED = 42
MAX_EPOCHS = 600
LEARNING_RATE = 0.001
HIDDEN_SIZE = 16
TARGET_LOSS = 0.0025
PLATEAU_PATIENCE = 60
MIN_IMPROVEMENT = 1e-4


def _set_training_seed():
    random.seed(TRAINING_RANDOM_SEED)
    np.random.seed(TRAINING_RANDOM_SEED)
    torch.manual_seed(TRAINING_RANDOM_SEED)


def needs_retraining():
    if not os.path.exists(MODEL_DATA_PATH):
        return True
    try:
        return os.path.getmtime(INTENTS_PATH) > os.path.getmtime(MODEL_DATA_PATH)
    except OSError:
        return True


def _load_intents():
    with open(INTENTS_PATH, "r", encoding="utf-8") as file_handle:
        data = json.load(file_handle)

    intents = data.get("intents")
    if not isinstance(intents, list) or not intents:
        raise ValueError("No intents were found in the training file.")
    return intents


def _prepare_training_data(intents):
    all_words = []
    tags = []
    pairs = []

    for intent in intents:
        tag = str(intent.get("tag", "")).strip()
        patterns = intent.get("patterns", [])
        if not tag or not patterns:
            continue

        tags.append(tag)
        for pattern in patterns:
            tokens = tokenize(str(pattern))
            if not tokens:
                continue
            all_words.extend(tokens)
            pairs.append((tokens, tag))

    if not pairs:
        raise ValueError("No valid training patterns were found.")

    all_words = sorted({stem(word) for word in all_words if word not in IGNORE_WORDS})
    tags = sorted(set(tags))

    x_train = []
    y_train = []
    tag_to_index = {tag: index for index, tag in enumerate(tags)}
    for pattern_tokens, tag in pairs:
        x_train.append(bag_of_words(pattern_tokens, all_words))
        y_train.append(tag_to_index[tag])

    features = torch.tensor(np.array(x_train), dtype=torch.float32)
    labels = torch.tensor(y_train, dtype=torch.long)
    return features, labels, all_words, tags


def run_training(force=False):
    """Train the local model when intents changed or no model exists."""
    if not force and not needs_retraining():
        print("--- TRAINING SKIPPED | Existing model is up to date. ---")
        return False

    _set_training_seed()
    print("--- STARTING BRAIN TRAINING ---")

    intents = _load_intents()
    x_train, y_train, all_words, tags = _prepare_training_data(intents)

    input_size = x_train.shape[1]
    output_size = len(tags)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    features = x_train.to(device)
    labels = y_train.to(device)
    model = NeuralNet(input_size, HIDDEN_SIZE, output_size).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=LEARNING_RATE)

    best_loss = float("inf")
    stale_epochs = 0

    for epoch in range(MAX_EPOCHS):
        outputs = model(features)
        loss = criterion(outputs, labels)

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        loss_value = float(loss.item())
        if loss_value + MIN_IMPROVEMENT < best_loss:
            best_loss = loss_value
            stale_epochs = 0
        else:
            stale_epochs += 1

        if (epoch + 1) % 100 == 0:
            print(f"Epoch [{epoch + 1}/{MAX_EPOCHS}], Loss: {loss_value:.6f}")

        if best_loss <= TARGET_LOSS or stale_epochs >= PLATEAU_PATIENCE:
            break

    data = {
        "model_state": model.state_dict(),
        "input_size": input_size,
        "hidden_size": HIDDEN_SIZE,
        "output_size": output_size,
        "all_words": all_words,
        "tags": tags,
    }

    os.makedirs(os.path.dirname(MODEL_DATA_PATH), exist_ok=True)
    temp_path = f"{MODEL_DATA_PATH}.tmp"
    torch.save(data, temp_path)
    os.replace(temp_path, MODEL_DATA_PATH)
    print(f"--- TRAINING COMPLETE | Final Loss: {best_loss:.6f} ---")
    return True
