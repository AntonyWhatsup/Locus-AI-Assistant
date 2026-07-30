# Technical Information

## Architecture Overview

Locus is a local desktop application composed of five main layers:

1. `main.py` starts FastAPI, serves the React build, opens PyWebView, prepares the local model, and optionally starts wake-word listening.
2. `frontend/` contains the React UI that connects to the backend over WebSocket.
3. `src/api_manager.py` broadcasts backend state changes to connected UI clients.
4. `src/processor.py` captures microphone input, runs local inference, and coordinates command handling.
5. `src/actions.py` resolves recognized intents into Chrome actions, MCP calls, Gemini calls, or exit behavior.

## Runtime Flow

```text
main.py
  -> apply_settings()
  -> reload_gemini_client()
  -> run_training() when model data is missing or stale
  -> reload_model()
  -> background_listener() only when LOCUS_ENABLE_CLOUD_WAKE_LISTENER=1
  -> websocket / listen action
      -> manual_activation()
      -> listen_and_process()
          -> tokenize + bag_of_words
          -> NeuralNet inference
          -> execute_command_logic()
  -> websocket / stop action
      -> stop_activation()
      -> cooperative cancellation event
```

## WebSocket Security Model

`/ws` is protected by two local checks:

- Origin allowlist. Default allowed origins are `http://127.0.0.1:8000`, `http://localhost:8000`, `http://127.0.0.1:8443`, and `http://localhost:8443`. Add development origins with `LOCUS_ALLOWED_WS_ORIGINS`.
- Per-run session token. `main.py` generates a token at startup and serves it to allowed frontend origins through `/api/session`. The browser WebSocket connects with `/ws?token=...`.

The token is compatible with the browser WebSocket API and PyWebView because it is sent as a query parameter. It is runtime-only and must not be committed. `LOCUS_WS_TOKEN` exists only for controlled local testing.

Client commands are intentionally small:

```json
{"action":"listen"}
{"action":"stop"}
```

Invalid JSON, unknown actions, and unsupported fields return an `error` event. They do not start microphone capture.

## WebSocket Event Contract

The backend sends a full `snapshot` immediately after WebSocket connection, then incremental events:

| Type | Purpose |
|---|---|
| `snapshot` | Full UI recovery state: app state, status, mic state, image, mic level, visualizer, transcript, settings |
| `status` | User-facing status title, tone, and text |
| `mic_state` | Microphone state and detail message |
| `transcript` | Latest user and/or Locus text |
| `image` | Cat image state name |
| `mic_level` | Normalized microphone level from `0` to `1` |
| `visualizer` | Start/stop visualizer state and optional label |
| `command_ack` | Accepted/rejected command result |
| `error` | Controlled protocol error |
| `conversation_cleared` | Conversation panel should clear local history |

Canonical app states are `initializing`, `ready`, `listening`, `processing`, `speaking`, and `error`.

## Settings API

The Settings slide-over uses HTTP endpoints rather than separate WebSocket commands:

| Endpoint | Purpose |
|---|---|
| `GET /api/settings` | Load persisted runtime settings from `data/settings.json` or defaults |
| `GET /api/settings/options` | Load supported languages, themes, AI model metadata, and unavailable TTS state |
| `POST /api/settings` | Validate, save, and apply settings; requires `X-Locus-Session` |
| `POST /api/conversation/clear` | Clear the current conversation snapshot; requires `X-Locus-Session` |

Settings are validated by `src/settings_manager.py` before writing. Secrets are not returned from these endpoints. Gemini fallback can be selected only when `GEMINI_KEY` or `GEMINI_API_KEY` is configured.

## Main Modules

### `src/processor.py`

- Loads `data/data.pth` with `weights_only=True`
- Uses a processing lock to prevent overlapping microphone sessions
- Uses a cooperative cancellation event for the `stop` command
- Clears stale profile-selection context after timeout or unexpected errors
- Uses `torch.inference_mode()` during classification
- Keeps cloud wake-word listening opt-in

### `src/actions.py`

- Uses the current `google-genai` SDK
- Applies a Gemini request timeout through `HttpOptions`
- Keeps general Gemini fallback opt-in through `LOCUS_ENABLE_GEMINI_FALLBACK=1`
- Prefers standard Windows Chrome install paths before falling back to `PATH`
- Routes MCP requests when MCP is explicitly enabled in settings

### `src/brain/trainer_module.py`

- Retrains only when `data/data.pth` is missing or older than `src/brain/intents.json`
- Uses deterministic seeds
- Stops early when the target loss or plateau condition is reached
- Saves generated model data atomically

## Important Paths

| Path | Purpose |
|---|---|
| `frontend/src/` | React source |
| `frontend/package-lock.json` | Frontend dependency lockfile |
| `requirements.txt` | Python dependency manifest |
| `scripts/debug_gemini.py` | Gemini connectivity check |
| `src/brain/intents.json` | Intent dataset |
| `data/data.pth` | Generated trained model, ignored by git |
| `data/settings.json` | Generated local settings, ignored by git |
| `logs/` | Local logs, ignored by git |

## Current Constraints

- Chrome launch behavior is Windows-specific.
- Speech recognition depends on microphone availability and network-backed recognition.
- Cloud wake-word listening is disabled by default because it sends ambient snippets to Google Speech Recognition.
- General Gemini fallback is disabled by default because it can send unsupported dictated text to Gemini.
