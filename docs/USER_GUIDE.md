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
2. The desktop launcher waits for `/health` to respond.
3. PyWebView opens the local React UI.
4. The local intent model retrains only if `data/data.pth` is missing or stale.
5. The model is loaded.
6. Optional background wake-word listening starts only when `LOCUS_ENABLE_CLOUD_WAKE_LISTENER=1`.

## How To Activate Locus

- Click the listen control in the UI.
- Optionally say `Locus`, `local`, `locust`, or `focus` after enabling `LOCUS_ENABLE_CLOUD_WAKE_LISTENER=1`.

By default, manual activation is the privacy-preserving path. Cloud wake-word listening uses Google Speech Recognition before the wake word is known. General Gemini fallback for unsupported dictated text is also opt-in via `LOCUS_ENABLE_GEMINI_FALLBACK=1`.

## Settings

Open Settings from the Assistant card or the `SET` item in the sidebar. The panel opens from the right and keeps unsaved edits in a draft until `Save changes`.

Available settings:

- Voice & Wake: wake words, microphone sensitivity, language, auto-listen on startup, live transcript display.
- AI Model: local model or Gemini fallback when a Gemini API key is configured. OpenAI is shown as unavailable because this backend does not implement it.
- Appearance: Glass Green, Dark, Light, Colorful, and Nyan themes. Theme names are saved with canonical values such as `glass-green` and `cat`.
- Advanced: debug mode, local intent cache, and confirmed conversation-history clearing.

TTS voice selection is displayed as unavailable because this backend does not currently implement TTS voice management.

## Frontend Development And WebSocket Configuration

The production frontend is served by FastAPI. For local frontend development, run Vite in `frontend/` and point it at the backend when needed:

```powershell
cd frontend
npm install
npm run dev
```

Useful environment variables:

| Variable | Purpose |
|---|---|
| `LOCUS_PORT` | Backend port, default `8000` |
| `LOCUS_ALLOWED_WS_ORIGINS` | Comma-separated extra allowed browser origins for `/ws` and `/api/session` |
| `LOCUS_WS_TOKEN` | Optional fixed WebSocket token for controlled local testing only |
| `VITE_LOCUS_API_BASE_URL` | Frontend API base URL override |
| `VITE_LOCUS_WS_URL` | Frontend WebSocket URL override |

The backend generates a local session token on startup. The frontend gets it from `/api/session` and then connects to `/ws?token=...`. Do not store that token in source control.

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
- If Vite cannot connect to the backend WebSocket, add the Vite origin to `LOCUS_ALLOWED_WS_ORIGINS`.

## Local Verification

```powershell
python -B -m unittest discover -s tests
```
