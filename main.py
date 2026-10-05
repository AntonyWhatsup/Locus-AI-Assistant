import asyncio
import json
import threading
import uvicorn
from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import time
import urllib.request
import webview

import src.config as config
from src.api_manager import api_manager
from src.processor import background_listener, reload_model, manual_activation, stop_activation
from src.brain.trainer_module import run_training
from src.actions import reload_gemini_client
from src.settings_manager import (
    AI_MODEL_OPTIONS,
    LANGUAGE_OPTIONS,
    THEME_OPTIONS,
    apply_settings,
    load_gemini_api_key,
    load_settings,
    save_settings,
    validate_settings_input,
)
from src.ws_protocol import allowed_origins, generate_session_token, is_allowed_origin, normalize_theme, validate_command

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    api_manager.set_loop(asyncio.get_running_loop())
    apply_settings(load_settings())
    api_manager.sync_settings()
    reload_gemini_client()
    start_sequence(api_manager)
    print(f"Backend ready at http://{HOST}:{PORT}")
    yield

app = FastAPI(lifespan=lifespan)
SESSION_TOKEN = generate_session_token()
HOST = "127.0.0.1"
PORT = int(os.getenv("LOCUS_PORT", "8000"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=sorted(allowed_origins()),
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

def start_sequence(ui):
    ui.root.after(0, lambda: ui.fade_to_image("train"))
    ui.root.after(0, lambda: ui.set_status("Preparing brain...", "thinking", "Checking whether the local intent model needs retraining."))
    ui.root.after(0, lambda: ui.set_mic_state("thinking", "Checking whether the local intent model needs retraining."))

    def task():
        try:
            trained = run_training()
            reload_ok = reload_model()
            if not reload_ok:
                ui.root.after(0, lambda: ui.set_status("Brain load failed", "error", "The local model could not be loaded."))
                ui.root.after(0, lambda: ui.set_transcript(locus_text="The local intent model failed to load. Check the console for details."))
                return

            if trained:
                ui.root.after(0, lambda: ui.set_status("Brain updated", "success", "The local intent model was retrained successfully."))
            else:
                ui.root.after(0, lambda: ui.set_status("Brain ready", "success", "The cached local intent model is already up to date."))
        except Exception as exc:
            print(f"Training Failed: {exc}")
            ui.root.after(0, lambda: ui.set_status("Startup failed", "error", "The local model could not be prepared."))
            ui.root.after(0, lambda: ui.set_transcript(locus_text="Startup failed while preparing the local model."))
            return

        ui.root.after(0, lambda: ui.fade_to_image("idle"))
        ui.root.after(0, lambda: ui.set_mic_state("idle", "Ready for the next wake word."))
        if config.CLOUD_WAKE_LISTENER_ENABLED:
            ui.root.after(0, lambda: ui.set_status("Say 'Locus'", "idle", "Click the cat or wait for the wake word."))
            threading.Thread(target=background_listener, args=(ui,), daemon=True).start()
        else:
            ui.root.after(0, lambda: ui.set_status("Click to listen", "idle", "Cloud wake-word listening is disabled by default."))

    threading.Thread(target=task, daemon=True).start()



@app.get("/health")
async def health():
    return {"ok": True, "state": api_manager.snapshot().app_state}


@app.get("/api/session")
async def session(request: Request):
    origin = request.headers.get("origin")
    if origin and origin.rstrip("/") not in allowed_origins():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Origin is not allowed.")
    return {"ws_token": SESSION_TOKEN, "ws_path": "/ws"}


@app.get("/api/settings")
async def get_settings():
    return load_settings()


@app.get("/api/settings/options")
async def get_settings_options():
    return {
        "languages": LANGUAGE_OPTIONS,
        "themes": THEME_OPTIONS,
        "ai_models": {
            **AI_MODEL_OPTIONS,
            "openai": {"label": "OpenAI", "disabled": True, "reason": "OpenAI integration is not implemented in this backend."},
        },
        "tts_voices": [],
        "tts_voice_unavailable_reason": "Text-to-speech voice selection is not implemented in this backend.",
    }


@app.post("/api/settings")
async def update_settings(request: Request):
    token = request.headers.get("x-locus-session")
    if token != SESSION_TOKEN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid session token.")
    payload = await request.json()
    current = load_settings()
    next_settings = {**current, **payload}
    next_settings["theme"] = normalize_theme(next_settings.get("theme"))
    validation = validate_settings_input(next_settings)
    if not validation.is_valid:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=validation.errors)
    if next_settings.get("ai_model") == "gemini" and not load_gemini_api_key():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"ai_model": "Gemini fallback requires GEMINI_KEY or GEMINI_API_KEY in .env."},
        )
    saved = save_settings(next_settings)
    apply_settings(saved)
    api_manager.set_theme(saved["theme"])
    return saved


@app.post("/api/conversation/clear")
async def clear_conversation(request: Request):
    token = request.headers.get("x-locus-session")
    if token != SESSION_TOKEN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid session token.")
    api_manager.clear_conversation()
    return {"ok": True}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    if not is_allowed_origin(websocket):
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    if websocket.query_params.get("token") != SESSION_TOKEN:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await api_manager.connect(websocket)
    try:
        while True:
            message = await websocket.receive()
            if message.get("type") == "websocket.disconnect":
                break
            raw_message = message.get("text")
            if raw_message is None:
                await api_manager.send_error(websocket, "invalid_message", "Message must be a text JSON frame.")
                continue
            try:
                data = json.loads(raw_message)
            except json.JSONDecodeError:
                await api_manager.send_error(websocket, "invalid_json", "Message must be valid JSON.")
                continue

            action, error = validate_command(data)
            if error:
                await api_manager.send_error(websocket, "invalid_command", error)
                continue

            if action == "listen":
                manual_activation(api_manager)
            elif action == "stop":
                stop_activation(api_manager)
    except WebSocketDisconnect:
        pass
    finally:
        api_manager.disconnect(websocket)

if os.path.exists("frontend/dist"):
    app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="static")

def run_server():
    config_obj = uvicorn.Config(app, host=HOST, port=PORT, log_level="error")
    server = uvicorn.Server(config_obj)
    api_manager.server = server
    server.run()


def wait_for_server(timeout=15.0):
    deadline = time.monotonic() + timeout
    url = f"http://{HOST}:{PORT}/health"
    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=0.5) as response:
                if response.status == 200:
                    return True
        except Exception:
            time.sleep(0.2)
    return False

if __name__ == "__main__":
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()

    if not wait_for_server():
        raise RuntimeError("Locus backend did not become ready in time.")

    try:
        webview.create_window("Locus AI", f"http://{HOST}:{PORT}", width=1320, height=820, min_size=(920, 640))
        webview.start()
    finally:
        stop_activation(api_manager)
        server = getattr(api_manager, "server", None)
        if server is not None:
            server.should_exit = True
