import asyncio
import threading
import webbrowser
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles

from src.api_manager import api_manager
from src.processor import background_listener, reload_model, manual_activation
from src.brain.trainer_module import run_training
from src.actions import reload_gemini_client
from src.settings_manager import apply_settings, load_settings

app = FastAPI()

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
        ui.root.after(0, lambda: ui.set_status("Say 'Locus'", "idle", "Click the cat or wait for the wake word."))

        threading.Thread(target=background_listener, args=(ui,), daemon=True).start()

    threading.Thread(target=task, daemon=True).start()

@app.on_event("startup")
async def startup_event():
    api_manager.set_loop(asyncio.get_running_loop())
    
    apply_settings(load_settings())
    reload_gemini_client()
    start_sequence(api_manager)
    print("Backend ready. Open browser to http://localhost:8000")
    try:
        webbrowser.open("http://localhost:8000")
    except Exception:
        pass

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await api_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            if data.get("action") == "listen":
                manual_activation(api_manager)
    except WebSocketDisconnect:
        api_manager.disconnect(websocket)

# Optionally serve static files if dist exists
import os
if os.path.exists("frontend/dist"):
    app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="static")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
