# User Guide

## Purpose

Locus is a desktop voice assistant with a cat-themed React interface. It handles a small set of commands locally, can call a configured MCP tool, and can optionally send conversational requests to Google Gemini.

## Before You Start

- Python 3.10 or newer
- Windows
- Node.js/npm for building the frontend
- A working microphone
- Dependencies installed with `pip install -r requirements.txt`
- Frontend built with `npm install` and `npm run build` inside `frontend/`
- A `.env` file with `GEMINI_KEY` or `GEMINI_API_KEY` if Gemini features are used

## Starting the App

Run:

```powershell
python main.py
```

Startup flow:

1. FastAPI starts on `127.0.0.1:8000`.
2. PyWebView opens the local React UI.
3. The local intent model retrains only if `data/data.pth` is missing or stale.
4. The model is loaded.
5. Optional background wake-word listening starts only when `LOCUS_ENABLE_CLOUD_WAKE_LISTENER=1`.

## How To Activate Locus

- Click the listen control in the UI.
- Optionally say `Locus`, `local`, `locust`, or `focus` after enabling `LOCUS_ENABLE_CLOUD_WAKE_LISTENER=1`.

By default, manual activation is the privacy-preserving path. Cloud wake-word listening uses Google Speech Recognition before the wake word is known. General Gemini fallback for unsupported dictated text is also opt-in via `LOCUS_ENABLE_GEMINI_FALLBACK=1`.

## Supported Commands

| Phrase | Result |
|---|---|
| `Open browser` or `Start Chrome` | Prompts for a Chrome profile and opens Chrome |
| `Open YouTube` | Prompts for a Chrome profile and opens YouTube |
| `Anton`, `Anthony`, `Tony` | Selects the Anton profile |
| `Clean`, `Mr Clean` | Selects the Mr Clean profile |
| `Default`, `Normal`, `Main` | Selects the default profile |
| `Project status` | Calls the bundled MCP status tool when configured |
| `How are you?` | Sends a short playful request to Gemini |
| `Bye`, `Goodbye`, `Exit` | Closes the application |
| Other recognized speech | Can route to MCP, or to Gemini only when opt-in fallback is enabled |

## Troubleshooting

- If the microphone fails, verify device access and Windows audio permissions.
- If Gemini replies fail, confirm `GEMINI_KEY` or `GEMINI_API_KEY` is set correctly in `.env`.
- If Chrome does not open, check the profile mapping in `src/config.py`.
- If the UI is blank, run `npm install` and `npm run build` in `frontend/`.
- If the app does not recognize expected commands, review `src/brain/intents.json`.

## Local Verification

```powershell
python -B -m unittest discover -s tests
```
