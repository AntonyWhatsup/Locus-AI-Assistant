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

