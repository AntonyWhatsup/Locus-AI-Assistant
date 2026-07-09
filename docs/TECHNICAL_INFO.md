# Technical Information

## Architecture Overview

Locus is a local desktop application composed of four main layers:

1. `main.py` boots the UI, triggers retraining, reloads the model, and starts the background listener.
2. `src/ui_manager.py` owns the Tkinter window, image transitions, settings dialog, and visual feedback.
3. `src/processor.py` captures microphone input, runs inference, and coordinates UI state changes.
4. `src/actions.py` resolves recognized intents into browser actions, Gemini requests, or exit behavior.

## Runtime Flow

```text
main.py
  -> run_training()
  -> reload_model()
  -> background_listener()
      -> listen_and_process()
          -> tokenize + bag_of_words
          -> NeuralNet inference
          -> execute_command_logic()
```

## Main Modules

### `main.py`

- Initializes the Tkinter root window
- Creates the `LocusUI` instance
- Binds left-click manual activation
- Starts training and the background listener sequence

### `src/ui_manager.py`

- Displays cat-state images from `assets/`
- Animates transitions with `fade_to_image()`
- Shows a simple level visualizer while listening
- Exposes a settings dialog for runtime-only updates to language and wake words

### `src/processor.py`

- Loads the trained model from `data/data.pth`
- Uses `speech_recognition` for audio capture and speech-to-text
- Converts text into bag-of-words vectors
- Applies the trained PyTorch model to classify intents
- Maintains conversational context for profile selection flows

### `src/actions.py`

- Configures Gemini when `GEMINI_KEY` is available
- Detects the local Chrome executable
- Maps intent tags to Chrome launch actions, Gemini prompts, or exit behavior

### `src/brain/trainer_module.py`

- Loads `src/brain/intents.json`
- Builds the vocabulary and training pairs
- Trains a three-layer feedforward network
- Saves weights and metadata to `data/data.pth`

## Model Details

### Training Inputs

- Source data: `src/brain/intents.json`
- Text preprocessing: tokenization, stemming, bag-of-words encoding
- Labels: one class per intent tag

### Network Shape

- Input: vocabulary-sized bag-of-words vector
- Hidden layer: 16 units
- Hidden layer: 16 units
- Output: number of intent tags

### Training Settings

- Framework: PyTorch
- Loss: `CrossEntropyLoss`
- Optimizer: Adam
- Learning rate: `0.001`
- Epochs: `1200`

## Important Paths

| Path | Purpose |
|---|---|
| `assets/` | Cat-state images used by the UI |
| `scripts/debug_gemini.py` | Quick Gemini connectivity check |
| `src/config.py` | Runtime defaults and file paths |
| `src/brain/intents.json` | Intent dataset |
| `data/data.pth` | Generated trained model |
| `logs/` | Project-local logs |

## Current Constraints

- Chrome launch behavior is Windows-specific.
- Runtime settings changes are not persisted to disk.
- Speech recognition depends on microphone availability and network-backed recognition.
- The model is retrained on every startup rather than incrementally updated.
