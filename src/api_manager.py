import asyncio
import json
import os
import threading

import src.config as config
from src.ws_protocol import (
    CommandAckEvent,
    ErrorEvent,
    ImageEvent,
    MicLevelEvent,
    MicStateEvent,
    RuntimeState,
    StatusEvent,
    TranscriptEvent,
    VisualizerEvent,
    event_to_dict,
    make_snapshot,
    normalize_theme,
)

class MockRoot:
    def after(self, ms, func):
        func()
    def quit(self):
        os._exit(0)

class APIManager:
    def __init__(self):
        self.active_connections = []
        self.loop = None
        self.root = MockRoot()
        self._state_lock = threading.Lock()
        self.state = RuntimeState()
    
    def set_loop(self, loop):
        self.loop = loop

    async def connect(self, websocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        await websocket.send_text(json.dumps(make_snapshot(self.snapshot())))

    def disconnect(self, websocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    def snapshot(self):
        with self._state_lock:
            return self.state

    def _update_state(self, **changes):
        with self._state_lock:
            self.state = RuntimeState(**{**self.state.__dict__, **changes})

    def send_error(self, websocket, code, message):
        event = ErrorEvent(type="error", code=code, message=message)
        return websocket.send_text(json.dumps(event_to_dict(event)))

    def command_ack(self, action, accepted, message):
        state = self.snapshot().app_state
        self._broadcast(event_to_dict(CommandAckEvent(type="command_ack", action=action, accepted=accepted, state=state, message=message)))

    def _broadcast(self, message: dict):
        if not self.loop or not self.loop.is_running():
            return
        
        async def _send():
            for connection in self.active_connections.copy():
                try:
                    await connection.send_text(json.dumps(message))
                except Exception:
                    if connection in self.active_connections:
                        self.active_connections.remove(connection)
        
        asyncio.run_coroutine_threadsafe(_send(), self.loop)

    def set_status(self, title, tone, text):
        event = StatusEvent(type="status", title=str(title), tone=tone, text=str(text))
        app_state = {
            "idle": "ready",
            "listening": "listening",
            "thinking": "processing",
            "speaking": "speaking",
            "success": "ready",
            "prompt": "listening",
            "error": "error",
        }.get(tone, self.snapshot().app_state)
        self._update_state(status=event, app_state=app_state)
        self._broadcast(event_to_dict(event))

    def set_mic_state(self, state, msg):
        event = MicStateEvent(type="mic_state", state=state, msg=str(msg))
        app_state = {
            "idle": "ready",
            "listening": "listening",
            "thinking": "processing",
            "speaking": "speaking",
            "success": "ready",
            "prompt": "listening",
            "error": "error",
        }.get(state, self.snapshot().app_state)
        self._update_state(mic_state=event, app_state=app_state)
        self._broadcast(event_to_dict(event))

    def set_transcript(self, user_text=None, locus_text=None):
        event = TranscriptEvent(type="transcript", user_text=user_text, locus_text=locus_text)
        changes = {}
        if user_text is not None:
            changes["user_text"] = str(user_text)
        if locus_text is not None:
            changes["locus_text"] = str(locus_text)
        self._update_state(**changes)
        self._broadcast(event_to_dict(event))

    def clear_conversation(self):
        self._update_state(user_text=None, locus_text=None)
        self._broadcast({"type": "conversation_cleared"})

    def fade_to_image(self, image_name):
        event = ImageEvent(type="image", image=str(image_name))
        self._update_state(image=str(image_name))
        self._broadcast(event_to_dict(event))

    def update_mic_level(self, level):
        normalized = min(1.0, max(0.0, float(level or 0.0)))
        event = MicLevelEvent(type="mic_level", level=normalized)
        self._update_state(mic_level=normalized)
        self._broadcast(event_to_dict(event))

    def start_visualizer(self, text=None):
        event = VisualizerEvent(type="visualizer", state="start", text=text)
        self._update_state(visualizer=event)
        self._broadcast(event_to_dict(event))

    def stop_visualizer(self):
        event = VisualizerEvent(type="visualizer", state="stop")
        self._update_state(visualizer=event, mic_level=0.0)
        self._broadcast(event_to_dict(event))
        self._broadcast(event_to_dict(MicLevelEvent(type="mic_level", level=0.0)))

    def set_theme(self, theme):
        canonical = normalize_theme(theme)
        self._update_state(theme=canonical)
        return canonical

    def sync_settings(self):
        self.set_theme(config.THEME)

api_manager = APIManager()
