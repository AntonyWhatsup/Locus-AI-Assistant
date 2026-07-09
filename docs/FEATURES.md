# Features

## Current Feature Set

### Core AI

- Offline intent classifier trained from a custom `intents.json` dataset
- NLTK-based tokenization, stemming, and bag-of-words preprocessing
- Automatic retraining on startup followed by model reload

### Voice Interaction

- Background wake-word listener
- Manual click-to-listen activation
- Speech-to-text processing through `speech_recognition`
- Context-aware follow-up flow for profile selection

### Actions

- Open Chrome with selected user profiles
- Open YouTube with selected user profiles
- Exit command handling
- Gemini fallback for unsupported or conversational requests

### User Interface

- Tkinter desktop window
- Animated state transitions between cat images
- Listening visualizer
- Runtime settings dialog for language and wake words

## Feature Status Notes

- Wake words currently default to `locus`, `local`, `locust`, and `focus`.
- Chrome profile support currently maps to Anton, Mr Clean, and Default.
- Settings updates apply only to the current session.
