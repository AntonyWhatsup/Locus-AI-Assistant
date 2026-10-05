import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

import main
import src.processor as processor
import src.config as config
from src.api_manager import APIManager


class ImmediateThread:
    def __init__(self, target=None, args=(), kwargs=None, daemon=None):
        self.target = target
        self.args = args
        self.kwargs = kwargs or {}
        self.daemon = daemon

    def start(self):
        if self.target:
            self.target(*self.args, **self.kwargs)


class WebSocketRuntimeTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.settings_path = Path(self.temp_dir.name) / "settings.json"
        self.settings_path_patcher = patch.object(config, "SETTINGS_PATH", str(self.settings_path))
        self.settings_path_patcher.start()
        self.addCleanup(self.settings_path_patcher.stop)
        self.original_start_sequence = main.start_sequence
        self.start_sequence_patcher = patch.object(main, "start_sequence", return_value=None)
        self.start_sequence_patcher.start()
        self.addCleanup(self.start_sequence_patcher.stop)
        main.api_manager.active_connections.clear()
        main.api_manager.state = APIManager().state

    def _client(self):
        return TestClient(main.app)

    def _ws_url(self):
        return f"/ws?token={main.SESSION_TOKEN}"

    def test_forbidden_origin_is_rejected(self):
        with self._client() as client:
            with self.assertRaises(WebSocketDisconnect):
                with client.websocket_connect(
                    self._ws_url(),
                    headers={"origin": "https://evil.example"},
                ):
                    pass

    def test_missing_or_wrong_token_is_rejected(self):
        with self._client() as client:
            with self.assertRaises(WebSocketDisconnect):
                with client.websocket_connect("/ws", headers={"origin": "http://127.0.0.1:8000"}):
                    pass

            with self.assertRaises(WebSocketDisconnect):
                with client.websocket_connect("/ws?token=wrong", headers={"origin": "http://127.0.0.1:8000"}):
                    pass

    def test_invalid_json_returns_controlled_error(self):
        with self._client() as client:
            with client.websocket_connect(self._ws_url(), headers={"origin": "http://127.0.0.1:8000"}) as websocket:
                websocket.receive_json()
                websocket.send_text("{not-json")
                response = websocket.receive_json()

        self.assertEqual(response["type"], "error")
        self.assertEqual(response["code"], "invalid_json")

    def test_unknown_command_returns_controlled_error(self):
        with self._client() as client:
            with client.websocket_connect(self._ws_url(), headers={"origin": "http://127.0.0.1:8000"}) as websocket:
                websocket.receive_json()
                websocket.send_json({"action": "dance"})
                response = websocket.receive_json()

        self.assertEqual(response["type"], "error")
        self.assertEqual(response["code"], "invalid_command")

    def test_listen_and_stop_commands_dispatch(self):
        with patch.object(main, "manual_activation", return_value=True) as listen, patch.object(
            main, "stop_activation", return_value=True
        ) as stop:
            with self._client() as client:
                with client.websocket_connect(self._ws_url(), headers={"origin": "http://127.0.0.1:8000"}) as websocket:
                    websocket.receive_json()
                    websocket.send_json({"action": "listen"})
                    websocket.send_json({"action": "stop"})

        listen.assert_called_once_with(main.api_manager)
        stop.assert_called_once_with(main.api_manager)

    def test_snapshot_is_sent_after_connect_and_reconnect(self):
        main.api_manager.set_status("Ready", "idle", "Ready for tests.")
        with self._client() as client:
            with client.websocket_connect(self._ws_url(), headers={"origin": "http://127.0.0.1:8000"}) as websocket:
                first = websocket.receive_json()
            with client.websocket_connect(self._ws_url(), headers={"origin": "http://127.0.0.1:8000"}) as websocket:
                second = websocket.receive_json()

        self.assertEqual(first["type"], "snapshot")
        self.assertEqual(first["status"]["title"], "Ready")
        self.assertEqual(second["type"], "snapshot")
        self.assertEqual(second["status"]["title"], "Ready")

    def test_repeated_listen_is_rejected_without_parallel_thread(self):
        processor.finish_processing()
        with patch.object(processor.threading, "Thread") as thread_class:
            thread_class.return_value.start.return_value = None
            first = processor.manual_activation(main.api_manager)
            second = processor.manual_activation(main.api_manager)

        self.assertTrue(first)
        self.assertFalse(second)
        thread_class.assert_called_once()
        processor.finish_processing()

    def test_stop_requests_cancellation(self):
        processor.finish_processing()
        with patch.object(processor.threading, "Thread") as thread_class:
            thread_class.return_value.start.return_value = None
            processor.manual_activation(main.api_manager)
            stopped = processor.stop_activation(main.api_manager)

        self.assertTrue(stopped)
        processor.finish_processing()

    def test_model_initialization_error_sets_error_snapshot(self):
        with patch.object(main.threading, "Thread", ImmediateThread), patch.object(main, "run_training", side_effect=RuntimeError("boom")):
            self.original_start_sequence(main.api_manager)

        snapshot = main.api_manager.snapshot()
        self.assertEqual(snapshot.app_state, "error")
        self.assertEqual(snapshot.status.title, "Startup failed")

    def test_settings_options_do_not_expose_secrets_and_mark_unsupported_modes(self):
        with self._client() as client:
            response = client.get("/api/settings/options")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("languages", payload)
        self.assertTrue(payload["ai_models"]["openai"]["disabled"])
        serialized = str(payload).lower()
        self.assertNotIn("gemini_key", serialized)
        self.assertNotIn("test-key", serialized)

    def test_settings_save_validates_payload_and_token(self):
        with self._client() as client:
            forbidden = client.post("/api/settings", json={"wake_words": ["locus"]})
            invalid = client.post(
                "/api/settings",
                headers={"x-locus-session": main.SESSION_TOKEN},
                json={"wake_words": [], "microphone_sensitivity": 120},
            )

        self.assertEqual(forbidden.status_code, 403)
        self.assertEqual(invalid.status_code, 422)
        self.assertIn("wake_words", invalid.json()["detail"])

    def test_settings_save_applies_runtime_values(self):
        with patch.object(main, "load_gemini_api_key", return_value=""):
            with self._client() as client:
                response = client.post(
                    "/api/settings",
                    headers={"x-locus-session": main.SESSION_TOKEN},
                    json={
                        "wake_words": ["Locus", "Focus"],
                        "language_code": "uk-UA",
                        "gemini_model": "gemini-test",
                        "theme": "nyan",
                        "animation_speed": "normal",
                        "microphone_sensitivity": 51,
                        "auto_listen_on_startup": True,
                        "show_live_transcript": False,
                        "ai_model": "local",
                        "debug_mode": True,
                        "local_intent_cache": False,
                    },
                )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["theme"], "cat")
        self.assertEqual(payload["wake_words"], ["locus", "focus"])
        self.assertEqual(config.MICROPHONE_SENSITIVITY, 51)
        self.assertFalse(config.SHOW_LIVE_TRANSCRIPT)

    def test_gemini_model_requires_configured_key(self):
        with patch.object(main, "load_gemini_api_key", return_value=""):
            with self._client() as client:
                response = client.post(
                    "/api/settings",
                    headers={"x-locus-session": main.SESSION_TOKEN},
                    json={"ai_model": "gemini"},
                )

        self.assertEqual(response.status_code, 422)
        self.assertIn("GEMINI_KEY", response.json()["detail"]["ai_model"])

    def test_clear_conversation_requires_token_and_clears_snapshot(self):
        main.api_manager.set_transcript(user_text="hello", locus_text="hi")
        with self._client() as client:
            forbidden = client.post("/api/conversation/clear")
            cleared = client.post("/api/conversation/clear", headers={"x-locus-session": main.SESSION_TOKEN})

        self.assertEqual(forbidden.status_code, 403)
        self.assertEqual(cleared.status_code, 200)
        snapshot = main.api_manager.snapshot()
        self.assertIsNone(snapshot.user_text)
        self.assertIsNone(snapshot.locus_text)


if __name__ == "__main__":
    unittest.main()
