# Locus AI Assistant

Locus is a desktop AI voice assistant with a visual cat theme. It classifies user intent using a lightweight offline feedforward neural network, falling back to Google's Gemini API for conversational prompts.

## 📖 Origin Story

Locus was originally conceived as a university project for a "Neural Networks" course. The core vision was to bridge the gap between complex technology and everyday users, specifically focusing on accessibility. The goal was to create a tool that simplifies device interaction and empowers individuals with special needs through intuitive voice control.

The name **Locus** was suggested by a colleague, drawing inspiration from the ancient mnemonic strategy known as the **Method of Loci** (often referred to as the *Memory Palace* technique). Just as a memory palace allows a person to effortlessly recall information by mentally navigating a familiar physical space, Locus is designed to help users navigate their digital environment. It acts as a cognitive extension—allowing users to simply speak their intent and instantly retrieve or activate the right tool in their "digital palace." What started as an academic assignment has evolved into a mission to make human-computer interaction as natural as recalling a memory.

---

## 📁 Project Structure

```
Locus_AI_Assistant/
├── main.py                    # Root entry point
├── README.md                  # Project overview and documentation
├── FEATURES.md                # Features status checklist
├── Read.me                    # Quick install instructions (raw notes)
├── .gitignore                 # Git ignored directories/files
├── assets/                    # Graphical cat image states
├── data/                      # Trained neural network weights
│   └── data.pth               # Generated training output
├── scripts/                   # Utility and diagnostic scripts
│   └── debug_gemini.py        # Verification script for Gemini API key
└── src/                       # Main application source code
    ├── __init__.py
    ├── config.py              # Configuration & Chrome Profile constants
    ├── ui_manager.py          # Tkinter window & visual transitions
    ├── actions.py             # OS actions & Gemini query handler
    ├── processor.py           # Audio capture & intent execution
    └── brain/                 # Deep Learning & NLP components
        ├── __init__.py
        ├── model.py           # Neural network model definition
        ├── nltk_utils.py      # Natural language preprocessing
        ├── trainer_module.py  # Intent classifier training pipeline
        └── intents.json       # Training samples and classes dataset
```

---

## 🛠️ Installation & Setup

1. **Python Virtual Environment:**
   ```bash
   python -m venv .venv
   .\.venv\Scripts\activate
   ```

2. **Dependencies:**
   Install required libraries:
   ```bash
   pip install torch torchvision torchaudio nltk numpy speechrecognition pyaudio pillow python-dotenv google-generativeai
   ```

3. **NLTK Data:**
   Download tokenization dictionaries:
   ```bash
   python -m nltk.downloader punkt_tab
   ```

4. **Environment Variables:**
   Create a `.env` file at the root directory and add your Google Gemini API key:
   ```env
   GEMINI_KEY=your_gemini_api_key_here
   ```

---

## 🚀 Running Locus

Start the assistant by executing the main script:
```bash
python main.py
```

### Usage
- On startup, the assistant dynamically updates and trains the Neural Network on your custom `intents.json`.
- Speak the wake word **"Locus"** (or local, locust, focus) or **left-click the cat image** to trigger manual listening mode.
- Give a voice command (e.g. *"Open YouTube"*). The assistant will ask you which Chrome profile to load (e.g. *"Anton"* or *"Clean"*).
- General conversation falls back to the Google Gemini LLM, which behaves like a sarcastic, funny cat assistant.

---

## 5. 📝 Raw Development Notes (Original `Read.me` content)

These are raw installation notes, some of which may be redundant with the "Installation & Setup" section, but are preserved for historical context.

```
встановити ці залежності
pip install torch torchvision torchaudio nltk numpy speechrecognition pyaudio

Відкрий термінал у папці D:\GitFile\Sieci-neuronowe і виконай:
git init
git add .
git commit -m "Initial commit: structure setup"
git checkout -b v0.0.1

на словник
python -m nltk.downloader punkt_tab

pip install pillow

віртуалка для пайтона 
python -m venv .venv

активація вірти 
.\.venv\Scripts\activate
```

---

# Technical Information about the "Locus AI" Project

This document provides a technical overview of the "Locus AI" project, based on the provided files.

## 1. General Overview

"Locus AI" appears to be a desktop application (likely Python-based with Tkinter) that integrates artificial intelligence/natural language processing (NLP) capabilities for user interaction. It includes a visual interface with animations and functionality for processing voice commands and executing actions.

## 2. Core Components and Their Functions

### 2.1. `main.py`
The main file for launching the application. It contains the `start_sequence` function, which initializes the UI and starts the main tasks of the program, including animation and potential command processing.

### 2.2. `src/ui_manager.py`
Responsible for managing the user interface.
*   **`LocusUI` Class**: The main UI class, using `tkinter`.
    *   Sets up the application window ("Locus AI v1.9 - Master"), its size, and background color.
    *   `fade_to_image` Method: Implements a smooth transition between images (e.g., `idle`, `listen`, `cool`, `train`), likely for visual indication of system status.
    *   `start_visualizer` and `stop_visualizer` Methods: Control an animation or visualization that runs in the background.

### 2.3. `src/brain/` - AI/NLP Components
This directory contains the core logic for natural language processing and machine learning models.

#### 2.3.1. `src/brain/model.py`
Defines the neural network architecture for intent classification or other NLP tasks.
*   **`NeuralNet` Class**: A `PyTorch` (`nn.Module`) based model.
    *   Consists of three linear layers (`l1`, `l2`, `l3`).
    *   Uses the `ReLU` activation function between layers.
    *   Designed to transform an input vector (`input_size`) into a class vector (`num_classes`) via a hidden layer (`hidden_size`).

#### 2.3.2. `src/brain/nltk_utils.py`
Utilities for text preprocessing, likely using the NLTK library.
*   `_getargspec_wrapper`: Helper function related to inspecting function arguments.
*   `tokenize(sentence)`: Splits a sentence into words (tokens).
*   `stem(word)`: Reduces a word to its base form (stem), likely to reduce vocabulary size and normalize text.
*   `bag_of_words(tokenized_sentence, words)`: Creates a "bag of words" vector for a sentence based on a given vocabulary, which is a common text representation for NLP models.

#### 2.3.3. `src/brain/trainer_module.py`
Contains functionality for training the AI model.
*   `run_training()`: A function that likely handles the process of training the neural network, using data from `intents.json` and utilities from `nltk_utils.py`.

#### 2.3.4. `src/brain/intents.json`
Likely a JSON format file containing user intent definitions, example phrases for each intent, and corresponding responses or actions. This is typical for chatbots and voice assistants.

### 2.4. `src/actions.py`
Defines actions that the system can perform based on recognized intents.
*   `ask_gemini(text)`: Function for interacting with the Gemini API (likely Google Gemini) to process queries or retrieve information.
*   `find_chrome()`: Function to detect and potentially launch the Google Chrome browser.
*   `execute_command_logic(tag, confidence, active_context)`: The main logic for executing commands based on the recognized intent (`tag`), confidence level (`confidence`), and current context (`active_context`).

### 2.5. `src/processor.py`
Responsible for processing input data (voice, text) and passing it to the AI model.
*   `reload_model()`: Reloads the AI model, possibly after changes or for updates.
*   `manual_activation(ui)`: Function for manual system activation, possibly via UI.
*   `listen_and_process(ui)`: The main function for listening to input (voice), processing it, and passing it to AI components.
*   `background_listener(ui)`: Function for background listening, allowing the system to continuously wait for commands.

### 2.6. `src/config.py`
Likely contains configuration parameters for the application, such as API keys, file paths, model settings, etc.

## 3. Dependencies (Anticipated)
*   **`tkinter`**: For creating the graphical user interface.
*   **`torch` / `torch.nn`**: For building and training neural networks.
*   **`nltk`**: For natural language processing (tokenization, stemming).
*   **Google Gemini API**: For functionality related to `ask_gemini`.
*   Likely other libraries for speech recognition, speech synthesis, file system operations, etc.

## 4. Resources and Assets
*   **`assets/`**: A directory containing images used in the UI (`cat_cool.jpg`, `cat_error.jpg`, `cat_idle.jpg`, `cat_listen.jpg`, `cat_success.jpg`, `cat_think.jpg`, `cat_train.jpg`). This indicates the use of visual indicators for system status.

## 5. Scripts
*   **`scripts/debug_gemini.py`**: A separate script for debugging interaction with the Gemini API.

## 6. Compiled Files
*   `__pycache__/` and its contents: Contains compiled Python files (`.pyc`), which are optimized bytecodes for faster startup.

