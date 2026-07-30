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
```

## Main Modules

### `src/processor.py`

- Loads `data/data.pth` with `weights_only=True`
- Uses a processing lock to prevent overlapping microphone sessions
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
