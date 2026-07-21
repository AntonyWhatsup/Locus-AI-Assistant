# Features

## Current Feature Set

### Core AI

- Offline intent classifier trained from a custom `intents.json` dataset
- NLTK-based tokenization, stemming, and bag-of-words preprocessing
- Automatic retraining only when generated model data is missing or stale

### Voice Interaction

- Manual click-to-listen activation
- Optional background wake-word listener, disabled by default for privacy
- Speech-to-text processing through `speech_recognition`
- Context-aware follow-up flow for Chrome profile selection

### Actions

- Open Chrome with selected user profiles
- Open YouTube with selected user profiles
- Exit command handling
- Optional MCP stdio tool calls
- Optional Gemini fallback for unsupported or conversational requests

### User Interface

- React UI served from a local FastAPI backend
- PyWebView desktop shell
- Animated cat-state feedback
- Listening visualizer
- Runtime settings dialog for voice, appearance, devices, Gemini, and MCP

## Feature Status Notes

- Wake words default to `locus`, `local`, `locust`, and `focus`.
- Chrome profile support maps to Anton, Mr Clean, and Default.
- Settings updates are saved to ignored local file `data/settings.json`.
- General Gemini fallback is opt-in with `LOCUS_ENABLE_GEMINI_FALLBACK=1`.
