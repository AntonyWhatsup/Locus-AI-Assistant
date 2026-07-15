import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import src.config as config
import src.settings_manager as settings_manager


class SettingsManagerTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)

        self.settings_path = Path(self.temp_dir.name) / "settings.json"
        self.env_path = Path(self.temp_dir.name) / ".env"
        self.original_runtime = {
            "LANG_CODE": config.LANG_CODE,
            "WAKE_WORDS": list(config.WAKE_WORDS),
            "MODEL_NAME": config.MODEL_NAME,
            "THEME": config.THEME,
            "ANIMATION_SPEED": config.ANIMATION_SPEED,
            "MICROPHONE_DEVICE_ID": config.MICROPHONE_DEVICE_ID,
            "OUTPUT_AUDIO_DEVICE_ID": config.OUTPUT_AUDIO_DEVICE_ID,
            "GOOGLE_API_KEY": config.GOOGLE_API_KEY,
            "MCP_SERVER_COMMAND": config.MCP_SERVER_COMMAND,
            "MCP_DEFAULT_TOOL": config.MCP_DEFAULT_TOOL,
            "MCP_ENABLED": config.MCP_ENABLED,
        }

        self.path_patcher = patch.object(config, "SETTINGS_PATH", str(self.settings_path))
        self.env_patcher = patch.object(config, "ENV_PATH", str(self.env_path))
        self.path_patcher.start()
        self.env_patcher.start()
        self.addCleanup(self.path_patcher.stop)
        self.addCleanup(self.env_patcher.stop)
        self.addCleanup(self._restore_runtime_config)

    def _restore_runtime_config(self):
        config.LANG_CODE = self.original_runtime["LANG_CODE"]
        config.WAKE_WORDS = list(self.original_runtime["WAKE_WORDS"])
        config.MODEL_NAME = self.original_runtime["MODEL_NAME"]
        config.THEME = self.original_runtime["THEME"]
        config.ANIMATION_SPEED = self.original_runtime["ANIMATION_SPEED"]
        config.MICROPHONE_DEVICE_ID = self.original_runtime["MICROPHONE_DEVICE_ID"]
        config.OUTPUT_AUDIO_DEVICE_ID = self.original_runtime["OUTPUT_AUDIO_DEVICE_ID"]
        config.GOOGLE_API_KEY = self.original_runtime["GOOGLE_API_KEY"]
        config.MCP_SERVER_COMMAND = self.original_runtime["MCP_SERVER_COMMAND"]
        config.MCP_DEFAULT_TOOL = self.original_runtime["MCP_DEFAULT_TOOL"]
        config.MCP_ENABLED = self.original_runtime["MCP_ENABLED"]

    def test_normalize_wake_words_splits_string_and_deduplicates(self):
        result = settings_manager._normalize_wake_words(" Locus, focus, LOCUS , local ")

        self.assertEqual(result, ["locus", "focus", "local"])

    def test_normalize_wake_words_falls_back_for_invalid_input(self):
        result = settings_manager._normalize_wake_words(None)

        self.assertEqual(result, [])

    def test_settings_defaults_returns_typed_defaults(self):
        defaults = settings_manager.Settings.defaults()

        self.assertEqual(defaults.to_dict(), dict(config.DEFAULT_SETTINGS))

    def test_validate_settings_accepts_valid_values_and_normalizes_fields(self):
        with patch.object(
            settings_manager.SettingsService,
            "list_input_audio_devices",
            return_value=[{"id": "USB Mic", "label": "USB Mic", "index": 0}],
        ), patch.object(
            settings_manager.SettingsService,
            "list_output_audio_devices",
            return_value=[{"id": "USB Speakers", "label": "USB Speakers", "index": 1}],
        ):
            raw_settings = {
                "language_code": "pl-PL",
                "wake_words": [" Locus ", "focus", "FOCUS"],
                "gemini_model": "gemini-test-model",
                "theme": "dark",
                "animation_speed": "fast",
                "microphone_device_id": "USB Mic",
                "output_audio_device_id": "USB Speakers",
                "mcp_server_command": "python scripts/mcp_project_server.py",
                "mcp_default_tool": "answer_project_question",
                "mcp_enabled": True,
            }

            validated = settings_manager.validate_settings(raw_settings)

        self.assertEqual(
            validated,
            {
                "language_code": "pl-PL",
                "wake_words": ["locus", "focus"],
                "gemini_model": "gemini-test-model",
                "theme": "dark",
                "animation_speed": "fast",
                "microphone_device_id": "USB Mic",
                "output_audio_device_id": "USB Speakers",
                "mcp_server_command": "python scripts/mcp_project_server.py",
                "mcp_default_tool": "answer_project_question",
                "mcp_enabled": True,
            },
        )

    def test_validate_settings_falls_back_for_invalid_fields_and_preserves_saved_devices_non_strictly(self):
        with patch.object(settings_manager.SettingsService, "list_input_audio_devices", return_value=[]), patch.object(
            settings_manager.SettingsService, "list_output_audio_devices", return_value=[]
        ):
            validated = settings_manager.validate_settings(
                {
                    "language_code": "   ",
                    "wake_words": "",
                    "gemini_model": "   ",
                    "theme": "neon",
                    "animation_speed": "warp",
                    "microphone_device_id": "Missing Mic",
                    "output_audio_device_id": "Missing Speaker",
                    "mcp_server_command": "  python scripts/mcp_project_server.py  ",
                    "mcp_default_tool": " answer_project_question ",
                    "mcp_enabled": "yes",
                }
            )

        expected = dict(config.DEFAULT_SETTINGS)
        expected["microphone_device_id"] = "Missing Mic"
        expected["output_audio_device_id"] = "Missing Speaker"
        expected["mcp_server_command"] = "python scripts/mcp_project_server.py"
        expected["mcp_default_tool"] = "answer_project_question"
        expected["mcp_enabled"] = True
        self.assertEqual(validated, expected)

    def test_validate_settings_input_returns_inline_errors_for_invalid_form_values(self):
        with patch.object(settings_manager.SettingsService, "list_input_audio_devices", return_value=[]), patch.object(
            settings_manager.SettingsService, "list_output_audio_devices", return_value=[]
        ):
            result = settings_manager.validate_settings_input(
                {
                    "language_code": "   ",
                    "wake_words": "",
                    "gemini_model": "   ",
                    "theme": "neon",
                    "animation_speed": "warp",
                    "microphone_device_id": "Missing Mic",
                    "output_audio_device_id": "Missing Speaker",
                }
            )

        self.assertFalse(result.is_valid)
        self.assertIsNone(result.settings)
        self.assertEqual(
            result.errors,
            {
                "language_code": "This field is required.",
                "wake_words": "Enter at least one wake word.",
                "gemini_model": "This field is required.",
                "theme": "Choose one of the available options.",
                "animation_speed": "Choose one of the available options.",
                "microphone_device_id": "Choose one of the available input audio devices.",
                "output_audio_device_id": "Choose one of the available output audio devices.",
            },
        )

    def test_validate_settings_input_returns_typed_settings_for_valid_form_values(self):
        with patch.object(
            settings_manager.SettingsService,
            "list_input_audio_devices",
            return_value=[{"id": "USB Mic", "label": "USB Mic", "index": 0}],
        ), patch.object(
            settings_manager.SettingsService,
            "list_output_audio_devices",
            return_value=[{"id": "USB Speakers", "label": "USB Speakers", "index": 1}],
        ):
            result = settings_manager.validate_settings_input(
                {
                    "language_code": "pl-PL",
                    "wake_words": "Locus, Focus",
                    "gemini_model": "gemini-form-test",
                    "theme": "dark",
                    "animation_speed": "fast",
                    "microphone_device_id": "USB Mic",
                    "output_audio_device_id": "USB Speakers",
                    "mcp_server_command": "python scripts/mcp_project_server.py",
                    "mcp_default_tool": "answer_project_question",
                    "mcp_enabled": True,
                }
            )

        self.assertTrue(result.is_valid)
        self.assertEqual(
            result.settings.to_dict(),
            {
                "language_code": "pl-PL",
                "wake_words": ["locus", "focus"],
                "gemini_model": "gemini-form-test",
                "theme": "dark",
                "animation_speed": "fast",
                "microphone_device_id": "USB Mic",
                "output_audio_device_id": "USB Speakers",
                "mcp_server_command": "python scripts/mcp_project_server.py",
                "mcp_default_tool": "answer_project_question",
                "mcp_enabled": True,
            },
        )

    def test_load_settings_validates_json_payload_from_disk(self):
        payload = {
            "language_code": "en-GB",
            "wake_words": "Locus, focus, focus",
            "gemini_model": "gemini-live",
            "theme": "glass_green",
            "animation_speed": "slow",
            "microphone_device_id": "Missing Mic",
            "output_audio_device_id": "Missing Speaker",
            "mcp_server_command": "python scripts/mcp_project_server.py",
            "mcp_default_tool": "project_status",
            "mcp_enabled": True,
        }
        self.settings_path.write_text(json.dumps(payload), encoding="utf-8")

        loaded = settings_manager.load_settings()

        self.assertEqual(
            loaded,
            {
                "language_code": "en-GB",
                "wake_words": ["locus", "focus"],
                "gemini_model": "gemini-live",
                "theme": "glass_green",
                "animation_speed": "slow",
                "microphone_device_id": "Missing Mic",
                "output_audio_device_id": "Missing Speaker",
                "mcp_server_command": "python scripts/mcp_project_server.py",
                "mcp_default_tool": "project_status",
                "mcp_enabled": True,
            },
        )

    def test_save_settings_creates_file_and_writes_validated_content(self):
        with patch.object(
            settings_manager.SettingsService,
            "list_input_audio_devices",
            return_value=[{"id": "USB Mic", "label": "USB Mic", "index": 0}],
        ), patch.object(
            settings_manager.SettingsService,
            "list_output_audio_devices",
            return_value=[{"id": "USB Speakers", "label": "USB Speakers", "index": 1}],
        ):
            result = settings_manager.save_settings(
                {
                    "language_code": "fr-FR",
                    "wake_words": "Locus, Focus",
                    "gemini_model": "gemini-save-test",
                    "theme": "light",
                    "animation_speed": "normal",
                    "microphone_device_id": "USB Mic",
                    "output_audio_device_id": "USB Speakers",
                    "mcp_server_command": "python scripts/mcp_project_server.py",
                    "mcp_default_tool": "project_status",
                    "mcp_enabled": True,
                }
            )

        saved_payload = json.loads(self.settings_path.read_text(encoding="utf-8"))
        expected = {
            "language_code": "fr-FR",
            "wake_words": ["locus", "focus"],
            "gemini_model": "gemini-save-test",
            "theme": "light",
            "animation_speed": "normal",
            "microphone_device_id": "USB Mic",
            "output_audio_device_id": "USB Speakers",
            "mcp_server_command": "python scripts/mcp_project_server.py",
            "mcp_default_tool": "project_status",
            "mcp_enabled": True,
        }

        self.assertEqual(result, expected)
        self.assertEqual(saved_payload, expected)

    def test_apply_settings_updates_runtime_config_values(self):
        with patch.object(
            settings_manager.SettingsService,
            "list_input_audio_devices",
            return_value=[{"id": "USB Mic", "label": "USB Mic", "index": 0}],
        ), patch.object(
            settings_manager.SettingsService,
            "list_output_audio_devices",
            return_value=[{"id": "USB Speakers", "label": "USB Speakers", "index": 1}],
        ):
            applied = settings_manager.apply_settings(
                {
                    "language_code": "de-DE",
                    "wake_words": "Locus, Local",
                    "gemini_model": "gemini-runtime-test",
                    "theme": "colorful",
                    "animation_speed": "slow",
                    "microphone_device_id": "USB Mic",
                    "output_audio_device_id": "USB Speakers",
                    "mcp_server_command": "python scripts/mcp_project_server.py",
                    "mcp_default_tool": "answer_project_question",
                    "mcp_enabled": True,
                }
            )

        self.assertEqual(applied["wake_words"], ["locus", "local"])
        self.assertEqual(config.LANG_CODE, "de-DE")
        self.assertEqual(config.WAKE_WORDS, ["locus", "local"])
        self.assertEqual(config.MODEL_NAME, "gemini-runtime-test")
        self.assertEqual(config.THEME, "colorful")
        self.assertEqual(config.ANIMATION_SPEED, "slow")
        self.assertEqual(config.MICROPHONE_DEVICE_ID, "USB Mic")
        self.assertEqual(config.OUTPUT_AUDIO_DEVICE_ID, "USB Speakers")
        self.assertEqual(config.MCP_SERVER_COMMAND, "python scripts/mcp_project_server.py")
        self.assertEqual(config.MCP_DEFAULT_TOOL, "answer_project_question")
        self.assertTrue(config.MCP_ENABLED)

    def test_load_gemini_api_key_reads_from_env_file(self):
        self.env_path.write_text("GEMINI_KEY=test-key\nOTHER=1\n", encoding="utf-8")

        api_key = settings_manager.load_gemini_api_key()

        self.assertEqual(api_key, "test-key")

    def test_save_gemini_api_key_updates_env_and_runtime_config(self):
        self.env_path.write_text("OTHER=1\n", encoding="utf-8")

        saved_key = settings_manager.save_gemini_api_key("new-secret")

        self.assertEqual(saved_key, "new-secret")
        self.assertEqual(config.GOOGLE_API_KEY, "new-secret")
        env_text = self.env_path.read_text(encoding="utf-8")
        self.assertIn("GEMINI_KEY=new-secret", env_text)
        self.assertIn("OTHER=1", env_text)

    def test_list_microphone_devices_filters_to_input_capable_devices(self):
        service = settings_manager.SettingsService()

        audio = unittest.mock.Mock()
        audio.get_device_count.return_value = 3
        audio.get_device_info_by_index.side_effect = [
            {"name": "USB Mic", "maxInputChannels": 1, "maxOutputChannels": 0},
            {"name": "Speakers", "maxInputChannels": 0, "maxOutputChannels": 2},
            {"name": "", "maxInputChannels": 2, "maxOutputChannels": 0},
        ]

        pyaudio_module = unittest.mock.Mock()
        pyaudio_module.PyAudio.return_value = audio

        with patch.object(settings_manager.sr.Microphone, "get_pyaudio", return_value=pyaudio_module):
            devices = service.list_microphone_devices()

        self.assertEqual(
            devices,
            [
                {"id": "USB Mic", "label": "USB Mic", "index": 0},
                {"id": "Input Device 2", "label": "Input Device 2", "index": 2},
            ],
        )

    def test_list_output_audio_devices_filters_to_output_capable_devices(self):
        service = settings_manager.SettingsService()

        audio = unittest.mock.Mock()
        audio.get_device_count.return_value = 3
        audio.get_device_info_by_index.side_effect = [
            {"name": "USB Mic", "maxInputChannels": 1, "maxOutputChannels": 0},
            {"name": "Speakers", "maxInputChannels": 0, "maxOutputChannels": 2},
            {"name": "", "maxInputChannels": 0, "maxOutputChannels": 1},
        ]

        pyaudio_module = unittest.mock.Mock()
        pyaudio_module.PyAudio.return_value = audio

        with patch.object(settings_manager.sr.Microphone, "get_pyaudio", return_value=pyaudio_module):
            devices = service.list_output_audio_devices()

        self.assertEqual(
            devices,
            [
                {"id": "Speakers", "label": "Speakers", "index": 1},
                {"id": "Output Device 2", "label": "Output Device 2", "index": 2},
            ],
        )


if __name__ == "__main__":
    unittest.main()
