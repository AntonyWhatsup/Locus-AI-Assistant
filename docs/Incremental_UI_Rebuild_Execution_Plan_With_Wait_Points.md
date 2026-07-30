# UI Integration Plan

This file supersedes the earlier desktop rebuild plan. Locus now uses a React/Vite frontend served by FastAPI and displayed in PyWebView.

## Current Priorities

1. Keep the React dashboard connected to real backend runtime state through the documented WebSocket contract.
2. Avoid fake metrics and no-op interactive controls.
3. Preserve local/offline rendering: required UI backgrounds and assets must be local CSS or local files.
4. Keep WebSocket access limited to allowed local origins and authenticated with a per-run session token.
5. Maintain responsive and keyboard-accessible controls without changing the visual direction unnecessarily.

## Verification Checkpoints

Use these commands after UI/backend integration changes:

```powershell
python -m compileall main.py src
python -B -m unittest discover -s tests
cd frontend
npm install
npx tsc --noEmit
npm run build
```

If audio, PyWebView, PyTorch, Gemini, or Windows-specific behavior cannot be exercised in the current environment, record the exact command that should be run on a local Windows desktop with the required devices and credentials.
