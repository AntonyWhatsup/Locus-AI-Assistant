import asyncio
import json
import os

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
    
    def set_loop(self, loop):
        self.loop = loop

    async def connect(self, websocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    def _broadcast(self, message: dict):
        if not self.loop:
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
        self._broadcast({"type": "status", "title": title, "tone": tone, "text": text})

    def set_mic_state(self, state, msg):
        self._broadcast({"type": "mic_state", "state": state, "msg": msg})

    def set_transcript(self, user_text=None, locus_text=None):
        self._broadcast({"type": "transcript", "user_text": user_text, "locus_text": locus_text})

    def fade_to_image(self, image_name):
        self._broadcast({"type": "image", "image": image_name})

    def update_mic_level(self, level):
        self._broadcast({"type": "mic_level", "level": level})

    def start_visualizer(self, text=None):
        self._broadcast({"type": "visualizer", "state": "start", "text": text})

    def stop_visualizer(self):
        self._broadcast({"type": "visualizer", "state": "stop"})

api_manager = APIManager()
