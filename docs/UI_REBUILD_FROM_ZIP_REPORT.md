# UI Rebuild Integration Report

## Current Architecture

The active UI is a React/Vite frontend served by the local FastAPI backend and displayed in PyWebView. The old desktop rebuild notes no longer describe the application architecture and should not be used as implementation guidance.

Current runtime targets:

- `main.py`: FastAPI, static frontend serving, WebSocket endpoint, PyWebView startup.
- `frontend/src/`: React dashboard and WebSocket client.
- `src/api_manager.py`: runtime state snapshot and backend-to-frontend events.
- `src/processor.py`: microphone capture, recognition, command execution, cooperative stop.

## Frontend And Backend Contract

The frontend connects to `/api/session` first, receives a per-run WebSocket token, then opens `/ws?token=...`. The backend sends a `snapshot` immediately after WebSocket accept, followed by incremental events.

Supported server event types:

- `snapshot`
- `status`
- `mic_state`
- `transcript`
- `image`
- `mic_level`
- `visualizer`
- `command_ack`
- `error`

Supported client commands:

- `{"action":"listen"}`
- `{"action":"stop"}`

Unknown commands and invalid JSON return controlled `error` events and do not start microphone capture.

## UI Status

- The dashboard keeps the existing visual direction and panel layout.
- `status`, `mic_level`, and `visualizer` are wired to real backend events.
- Session Summary no longer displays fake sessions, uptime, CPU, or RAM.
- Search, Settings, and unfinished sidebar destinations are disabled instead of acting as no-op clickable controls.
- Theme names are canonicalized as `glass-green`, `dark`, `light`, `colorful`, and `cat`; legacy `glass_green` and `nyan` values are still accepted.
- The Glass Green background is local CSS and does not depend on a remote image.

## Local Operation

Build the frontend before launching the desktop app:

```powershell
cd frontend
npm install
npm run build
cd ..
python main.py
```

During development, Vite can run separately. The frontend defaults to the current browser origin for `/api/session` and derives the WebSocket protocol from `http`/`https`. Override only when needed:

```env
VITE_LOCUS_API_BASE_URL=http://127.0.0.1:8000
VITE_LOCUS_WS_URL=ws://127.0.0.1:8000/ws
LOCUS_ALLOWED_WS_ORIGINS=http://127.0.0.1:8443,http://localhost:8443
LOCUS_PORT=8000
```

Do not commit local session tokens or credentials. WebSocket tokens are generated at process startup unless explicitly supplied through `LOCUS_WS_TOKEN` for controlled local testing.
