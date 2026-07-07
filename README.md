# 🐱 Locus AI Assistant

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python)
![PyTorch](https://img.shields.io/badge/PyTorch-2.x-EE4C2C?style=for-the-badge&logo=pytorch)
![Gemini](https://img.shields.io/badge/Google%20Gemini-API-4285F4?style=for-the-badge&logo=google)
![Tkinter](https://img.shields.io/badge/UI-Tkinter-informational?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

**A desktop AI voice assistant with a visual cat theme, powered by a custom offline neural network and Google Gemini.**

</div>

---

## 📖 Origin Story

Locus was originally conceived as a university project for a *"Neural Networks"* course. The core vision was to bridge the gap between complex technology and everyday users — specifically focusing on **accessibility**. The goal was to create a tool that simplifies device interaction and empowers individuals with special needs through intuitive voice control.

The name **Locus** was suggested by a colleague, drawing inspiration from the ancient mnemonic strategy known as the **Method of Loci** (often referred to as the *Memory Palace* technique). Just as a memory palace allows a person to effortlessly recall information by mentally navigating a familiar physical space, Locus is designed to help users navigate their digital environment. It acts as a cognitive extension — allowing users to simply speak their intent and instantly retrieve or activate the right tool in their "digital palace."

What started as an academic assignment has evolved into a mission to make human-computer interaction as natural as recalling a memory.

---

## ✨ Key Features

| Feature | Description |
|---|---|
| 🎙️ **Wake Word Detection** | Passively listens for "Locus" (+ similar sounds: local, locust, focus) |
| 🖱️ **Click-to-Listen** | Left-click the cat image to manually trigger listening mode |
| 🧠 **Offline Intent Classifier** | Lightweight 3-layer feedforward neural net (PyTorch) — runs fully offline |
| 💬 **Gemini LLM Fallback** | All unrecognized queries fall back to Google Gemini with a cat personality |
| 🌐 **Chrome Profile Launcher** | Opens Chrome with a specific user profile (Anton, Mr Clean, Default) |
| 📺 **YouTube Direct Launch** | Opens YouTube in the correct Chrome profile on voice command |
| 😺 **Visual Cat States** | Animated cat images reflect assistant state: idle, listen, think, train, cool, success, error |
| 🔁 **Auto-Training on Startup** | Neural network retrains from `intents.json` every time the app launches |
| ⚙️ **Settings Window** | Built-in settings panel accessible from the UI |

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        main.py (Entry)                      │
│  1. Launch Tkinter UI                                        │
│  2. Train Neural Net (background thread)                     │
│  3. Start Background Wake Word Listener                      │
└────────────────────────────┬────────────────────────────────┘
                             │
          ┌──────────────────┼──────────────────┐
          ▼                  ▼                  ▼
   ┌─────────────┐   ┌──────────────┐   ┌──────────────┐
   │ ui_manager  │   │  processor   │   │  brain/      │
   │  (Tkinter)  │   │  (Audio I/O) │   │  (PyTorch NN)│
   └─────────────┘   └──────┬───────┘   └──────────────┘
                            │
                   ┌────────┴────────┐
                   ▼                 ▼
            ┌──────────┐     ┌─────────────┐
            │ actions  │     │  Google      │
            │ (OS cmds)│     │  Gemini API  │
            └──────────┘     └─────────────┘
```

### Intent Processing Pipeline

```
Microphone Input
      │
      ▼
Google Speech Recognition (en-US)
      │
      ▼
Tokenize → Stem → Bag-of-Words Vector
      │
      ▼
NeuralNet (3-layer feedforward, ReLU)
      │
      ▼
Tag + Confidence Score
      │
      ├─ confidence > 0.60 → Execute OS Action (YouTube / Chrome)
      ├─ confidence > 0.20 → Send to Gemini LLM
      └─ confidence < 0.20 → "Unknown" state
```

---

## 📁 Project Structure

```
Locus_AI_Assistant/
├── main.py                    # Root entry point — initializes UI, training, listener
├── README.md                  # Full project documentation (this file)
├── Read.me                    # Original raw install notes (preserved for history)
├── .gitignore                 # Git ignored files and directories
│
├── assets/                    # Visual cat state images (JPG)
│   ├── cat_idle.jpg           # Default idle state
│   ├── cat_listen.jpg         # Actively listening
│   ├── cat_think.jpg          # Processing / awaiting input
│   ├── cat_train.jpg          # Neural network training in progress
│   ├── cat_cool.jpg           # "How are you?" cool response
│   ├── cat_success.jpg        # Command executed successfully
│   └── cat_error.jpg          # Error / microphone not found
│
├── data/
│   └── data.pth               # Trained neural network weights (auto-generated)
│
├── scripts/
│   └── debug_gemini.py        # Standalone script to verify Gemini API key
│
└── src/                       # Main application source code
    ├── __init__.py
    ├── config.py              # All constants: API keys, paths, wake words, Chrome profiles
    ├── ui_manager.py          # Tkinter window, image transitions, visualizer, settings panel
    ├── actions.py             # OS actions (Chrome launch) + Gemini LLM handler
    ├── processor.py           # Audio capture, wake word detection, intent execution loop
    └── brain/                 # Deep Learning & NLP subsystem
        ├── __init__.py
        ├── model.py           # NeuralNet class definition (PyTorch nn.Module)
        ├── nltk_utils.py      # Text preprocessing: tokenize(), stem(), bag_of_words()
        ├── trainer_module.py  # Full training pipeline: data prep → training → save
        └── intents.json       # Intent dataset: tags, patterns, responses
```

---

## 🛠️ Installation & Setup

### Prerequisites
- **Python 3.10+**
- **Windows OS** (Chrome path detection is Windows-specific)
- A working **microphone**
- A **Google Gemini API key** (free tier available at [aistudio.google.com](https://aistudio.google.com/))

---

### Step 1 — Clone the Repository

```bash
git clone https://github.com/AntonyWhatsup/Locus-AI-Assistant.git
cd Locus_AI_Assistant
```

### Step 2 — Create a Python Virtual Environment

```bash
python -m venv .venv
.\.venv\Scripts\activate
```

### Step 3 — Install Dependencies

```bash
pip install torch torchvision torchaudio nltk numpy speechrecognition pyaudio pillow python-dotenv google-generativeai
```

> **Note:** If `pyaudio` fails to install, download the correct `.whl` from [Christoph Gohlke's site](https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio) and install manually.

### Step 4 — Download NLTK Tokenizer Data

```bash
python -m nltk.downloader punkt_tab
```

### Step 5 — Configure the API Key

Create a `.env` file in the root directory:

```env
GEMINI_KEY=your_google_gemini_api_key_here
```

You can get a free key at [https://aistudio.google.com/](https://aistudio.google.com/).

---

## 🚀 Running Locus

```bash
python main.py
```

### What Happens at Startup

1. **UI launches** — the Tkinter window appears with the idle cat.
2. **Brain training** — the neural network auto-retrains on `intents.json` (takes ~5 seconds). The cat shows a "training" image.
3. **Model reload** — the freshly trained weights are loaded into memory.
4. **Idle mode** — the cat returns to idle and says *"Say 'Locus'"*.
5. **Background listener starts** — passively captures microphone audio waiting for the wake word.

---

## 🗣️ How to Use

### Wake Word
Say **"Locus"** (or anything that sounds like: *local*, *locust*, *focus*) to activate listening mode.

### Click-to-Listen
**Left-click the cat image** to manually trigger listening without the wake word. Useful in noisy environments.

### Voice Commands

| What You Say | What Happens |
|---|---|
| `"Open YouTube"` | Asks which Chrome profile → opens YouTube |
| `"Open browser"` / `"Start Chrome"` | Asks which Chrome profile → opens Chrome |
| `"Anton"` / `"Clean"` / `"Default"` | Selects a Chrome profile (when asked) |
| `"How are you?"` | Cat enters "cool" mode and replies via Gemini |
| `"Bye"` / `"Exit"` | Closes the application |
| *Anything else* | Sent to Google Gemini — answered in cat personality |

### Chrome Profiles

| Voice Command | Chrome Profile | Profile Folder |
|---|---|---|
| `"Anton"` / `"Anthony"` / `"Tony"` | Anton | `Profile 2` |
| `"Clean"` / `"Mr Clean"` | Mr Clean | `Profile 1` |
| `"Default"` / `"Normal"` / `"Main"` | Default | `Default` |

---

## 🧠 Neural Network Details

### Architecture — `NeuralNet` (`src/brain/model.py`)

```
Input Layer  →  [input_size]   (bag-of-words vector length)
Hidden Layer →  [16 neurons]   (ReLU activation)
Hidden Layer →  [16 neurons]   (ReLU activation)
Output Layer →  [num_classes]  (one output per intent tag)
```

- **Framework:** PyTorch (`torch.nn.Module`)
- **Activation:** ReLU (between hidden layers)
- **Loss Function:** CrossEntropyLoss (includes Softmax internally)
- **Optimizer:** Adam (`lr=0.001`)

### Training Pipeline — `trainer_module.py`

| Step | Description |
|---|---|
| **1. Load Data** | Reads `intents.json` — all tags and patterns |
| **2. Tokenize** | Each pattern is split into word tokens |
| **3. Stem** | Words are reduced to their base form (e.g., `opening` → `open`) |
| **4. Bag-of-Words** | Each sentence is converted to a binary vocabulary vector |
| **5. Train** | 1200 epochs, Adam optimizer, random seeds fixed for reproducibility |
| **6. Save** | Trained weights + metadata saved to `data/data.pth` |

### NLP Utilities — `nltk_utils.py`

| Function | Purpose |
|---|---|
| `tokenize(sentence)` | Splits text into word tokens using NLTK |
| `stem(word)` | Reduces word to base form (PorterStemmer) |
| `bag_of_words(tokens, vocab)` | Creates a binary vector representing word presence in vocabulary |

### Intent Dataset — `intents.json`

Each intent has:
- **`tag`** — unique identifier (e.g., `"open_youtube"`)
- **`patterns`** — list of example phrases that trigger this intent
- **`responses`** — placeholder responses (actual logic is in `actions.py`)

Current intents: `greeting`, `how_are_you`, `bye`, `open_browser`, `open_youtube`, `profile_anton`, `profile_mrclean`, `profile_default`

> You can add new intents by editing `src/brain/intents.json`. The model will retrain automatically on next launch.

---

## ⚙️ Configuration — `src/config.py`

| Constant | Default Value | Description |
|---|---|---|
| `GOOGLE_API_KEY` | from `.env` | Gemini API key |
| `MODEL_NAME` | `gemini-flash-latest` | Gemini model to use |
| `WAKE_WORDS` | `["locus", "local", "locust", "focus"]` | Trigger words |
| `LANG_CODE` | `"en-US"` | Speech recognition language |
| `CONNECTED_DEVICES` | Smart Bulb, Smart Plug | (Reserved for IoT expansion) |
| `CHROME_PROFILES` | Anton / Mr Clean / Default | Chrome user profile directories |
| `BASE_DIR` | root of project | Auto-resolved path |
| `ASSETS_DIR` | `assets/` | Cat image folder |
| `MODEL_DATA_PATH` | `data/data.pth` | Trained model save location |
| `INTENTS_PATH` | `src/brain/intents.json` | Intent training data |

---

## 🎨 UI States (Visual Cat Indicators)

| State | Image | Triggered When |
|---|---|---|
| `idle` | `cat_idle.jpg` | App is ready, waiting for wake word |
| `listen` | `cat_listen.jpg` | Actively listening to voice input |
| `think` | `cat_think.jpg` | Processing speech / awaiting profile choice |
| `train` | `cat_train.jpg` | Neural network is training at startup |
| `cool` | `cat_cool.jpg` | Responding to "how are you?" with Gemini |
| `success` | `cat_success.jpg` | Command executed successfully |
| `error` | `cat_error.jpg` | Microphone not found / error occurred |

Image transitions are animated via smooth fade in `ui_manager.py → fade_to_image()`.

---

## 🔍 Debugging

### Test Gemini API Key

```bash
python scripts/debug_gemini.py
```

This runs a standalone verification that your API key is valid and Gemini is reachable.

### Verbose Logs

The app prints structured logs to the console:

```
LOG: Brain reloaded (Continuous Mode).
LOG: Heard 'open youtube' -> open_youtube (0.94)
LOG: Launching Chrome with profile Profile 2
```

---

## 📦 Dependencies

| Package | Version | Purpose |
|---|---|---|
| `torch` + `torchvision` + `torchaudio` | 2.x | Neural network training and inference |
| `nltk` | latest | Tokenization and stemming |
| `numpy` | latest | Numerical arrays for training data |
| `speechrecognition` | latest | Microphone capture + Google Speech API |
| `pyaudio` | latest | Raw audio stream backend |
| `Pillow` | latest | Image loading and resizing for the UI |
| `python-dotenv` | latest | Loading `.env` API keys |
| `google-generativeai` | latest | Google Gemini API client |

---

## 🗺️ Roadmap

- [ ] Text-to-Speech (TTS) response output
- [ ] Expand intent library (music, smart home, system control)
- [ ] IoT integration (Smart Bulb / Smart Plug already reserved in config)
- [ ] Multi-language support (LANG_CODE already configurable)
- [ ] Packaging as a standalone `.exe` (PyInstaller)
- [ ] Hotkey support (keyboard shortcut to trigger listening)

---

## 📜 Changelog

### v2.0.0 (Current)
- Full project restructure and documentation overhaul
- Click-to-listen via cat image (`<Button-1>` binding)
- Settings window added to UI
- Improved error handling (microphone detection, Gemini fallback)
- Chrome profile multi-user support
- Auto-training pipeline on every launch

### v1.9 (Master)
- Core voice assistant functionality
- PyTorch intent classifier
- Gemini LLM fallback with cat personality
- Animated visual cat states

### v0.0.1 (Initial)
- University project skeleton
- Basic project structure setup

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Author

**Anton** — University project evolved into a passion project.  
Inspired by the Method of Loci (Memory Palace) technique.

> *"Meow? I mean... hello, human."* — Locus
