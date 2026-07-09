# Locus AI Assistant

Locus is a desktop voice assistant built with Python, Tkinter, PyTorch, and Google Gemini. It combines a small offline intent classifier with Gemini fallback responses and a cat-themed UI.

## Documentation Map

- [User Guide](docs/USER_GUIDE.md): how to run and use the assistant
- [Technical Information](docs/TECHNICAL_INFO.md): architecture, modules, and runtime flow
- [Features](docs/FEATURES.md): current capabilities and status
- [Ideas](docs/ideas.md): future improvements and expansion ideas
- [Legacy Setup Notes](Read.me): original setup notes preserved for reference

## Project Summary

- Wake-word activation with manual click-to-listen fallback
- Offline intent recognition backed by a small neural network
- Gemini responses for unsupported or conversational queries
- Chrome and YouTube launch flows with per-profile selection
- Animated cat-state UI for feedback during listening and processing

## Project Structure

```text
Locus_AI_Assistant/
|-- main.py
|-- README.md
|-- Read.me
|-- assets/
|-- docs/
|-- logs/
|-- scripts/
`-- src/
```

## Quick Start

1. Create a virtual environment:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\activate
   ```

2. Install dependencies:

   ```powershell
   pip install torch torchvision torchaudio nltk numpy speechrecognition pyaudio pillow python-dotenv google-generativeai
   ```

3. Download the NLTK tokenizer data:

   ```powershell
   python -m nltk.downloader punkt_tab
   ```

4. Create a `.env` file in the project root:

   ```env
   GEMINI_KEY=your_google_gemini_api_key_here
   ```

5. Run the app:

   ```powershell
   python main.py
   ```

## Requirements

- Python 3.10+
- Windows
- Working microphone
- Google Gemini API key

## Notes

- The model retrains on startup from `src/brain/intents.json`.
- Runtime settings changed in the UI are not written back to `src/config.py`.
- Logs are stored in the project-local `logs/` directory.
