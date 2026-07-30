import json
import os
import re
from dataclasses import asdict, dataclass
from typing import Dict, Mapping, Optional

import speech_recognition as sr
from dotenv import dotenv_values, set_key

import src.config as config


LANGUAGE_OPTIONS = {
    "en-US": {"label": "English (United States)"},
    "en-GB": {"label": "English (United Kingdom)"},
    "pl-PL": {"label": "Polish"},
    "uk-UA": {"label": "Ukrainian"},
    "de-DE": {"label": "German"},
    "fr-FR": {"label": "French"},
    "es-ES": {"label": "Spanish"},
    "it-IT": {"label": "Italian"},
}

WAKE_WORD_PRESET_OPTIONS = {
    "locus": {"label": "Locus"},
    "local": {"label": "Local"},
    "locust": {"label": "Locust"},
    "focus": {"label": "Focus"},
}

THEME_OPTIONS = {
    "glass_green": {
        "label": "Glass Green",
        "description": "Frosted dashboard with neon green accents",
    },
    "dark": {
        "label": "Dark",
        "description": "Low-light focused",
    },
    "light": {
        "label": "Light",
        "description": "Clean and minimal",
    },
    "colorful": {
        "label": "Colorful",
        "description": "Modern and playful",
    },
    "nyan": {
        "label": "Nyan 🐱",
        "description": "Vaporwave pink & purple with hot-pink accents",
    },
}

ANIMATION_SPEED_OPTIONS = {
    "slow": {"label": "Slow"},
    "normal": {"label": "Normal"},
    "fast": {"label": "Fast"},
}
MODEL_NAME_PATTERN = re.compile(r"^gemini-[a-z0-9][a-z0-9.\-]*$")
LANGUAGE_CODE_PATTERN = re.compile(r"^[a-z]{2,3}(?:-[A-Z]{2})?$")


@dataclass(frozen=True)
class Settings:
    language_code: str
    wake_words: list[str]
    gemini_model: str
    theme: str
    animation_speed: str
    microphone_device_id: str
    output_audio_device_id: str
    mcp_server_command: str
    mcp_default_tool: str
    mcp_enabled: bool

    @classmethod
    def defaults(cls):
        defaults = config.DEFAULT_SETTINGS
        return cls(
            language_code=str(defaults["language_code"]),
            wake_words=list(defaults["wake_words"]),
            gemini_model=str(defaults["gemini_model"]),
            theme=str(defaults["theme"]),
            animation_speed=str(defaults["animation_speed"]),
            microphone_device_id=str(defaults["microphone_device_id"]),
            output_audio_device_id=str(defaults["output_audio_device_id"]),
            mcp_server_command=str(defaults["mcp_server_command"]),
            mcp_default_tool=str(defaults["mcp_default_tool"]),
            mcp_enabled=bool(defaults["mcp_enabled"]),
        )

    def to_dict(self):
        return asdict(self)


@dataclass(frozen=True)
class ValidationResult:
    settings: Optional[Settings]
    errors: Dict[str, str]

    @property
    def is_valid(self):
        return not self.errors and self.settings is not None


def _normalize_wake_words(value):
    if isinstance(value, str):
        parts = value.split(",")
    elif isinstance(value, list):
        parts = value
    else:
        parts = []

    wake_words = []
    for part in parts:
        normalized = str(part).strip().lower()
        if normalized and normalized not in wake_words:
            wake_words.append(normalized)

    return wake_words


class SettingsService:
    def __init__(self, settings_path=None, env_path=None):
        self.settings_path = settings_path or config.SETTINGS_PATH
        self.env_path = env_path or config.ENV_PATH

    def defaults(self):
        return Settings.defaults()

    def load(self):
        if not os.path.exists(self.settings_path):
            return self.defaults()

        try:
            with open(self.settings_path, "r", encoding="utf-8") as file_handle:
                payload = json.load(file_handle)
        except (OSError, json.JSONDecodeError) as exc:
            print(f"Settings Load Error: {exc}")
            return self.defaults()

        return self._coerce(payload, strict=False)

    def validate(self, raw_settings):
        return self._validate(raw_settings)

    def save(self, settings):
        normalized = self._ensure_settings(settings)
        os.makedirs(os.path.dirname(self.settings_path), exist_ok=True)
        with open(self.settings_path, "w", encoding="utf-8") as file_handle:
            json.dump(normalized.to_dict(), file_handle, indent=2)
        return normalized

    def apply(self, settings):
        normalized = self._ensure_settings(settings)
        config.LANG_CODE = normalized.language_code
        config.WAKE_WORDS = list(normalized.wake_words)
        config.MODEL_NAME = normalized.gemini_model
        config.THEME = normalized.theme
        config.ANIMATION_SPEED = normalized.animation_speed
        config.MICROPHONE_DEVICE_ID = normalized.microphone_device_id
        config.OUTPUT_AUDIO_DEVICE_ID = normalized.output_audio_device_id
        config.MCP_SERVER_COMMAND = normalized.mcp_server_command
        config.MCP_DEFAULT_TOOL = normalized.mcp_default_tool
        config.MCP_ENABLED = normalized.mcp_enabled
        return normalized

    def load_gemini_api_key(self):
        env_values = dotenv_values(self.env_path)
        env_key = env_values.get("GEMINI_KEY") or env_values.get("GEMINI_API_KEY")
        if env_key is None:
            return str(config.GOOGLE_API_KEY or "").strip()
        return str(env_key).strip()

    def save_gemini_api_key(self, api_key):
        normalized = str(api_key or "").strip()
        set_key(self.env_path, "GEMINI_KEY", normalized, quote_mode="never")
        os.environ["GEMINI_KEY"] = normalized
        config.GOOGLE_API_KEY = normalized
        return normalized

    def list_microphone_devices(self):
        return self.list_input_audio_devices()

    def list_input_audio_devices(self):
        return self._list_audio_devices("input")

    def list_output_audio_devices(self):
        return self._list_audio_devices("output")

    def _list_audio_devices(self, direction):
        devices = []
        try:
            audio = sr.Microphone.get_pyaudio().PyAudio()
        except Exception as exc:
            print(f"Audio Device Load Error: {exc}")
            return devices

        try:
            seen_ids = set()
            for index in range(audio.get_device_count()):
                info = audio.get_device_info_by_index(index)
                if not self._is_device_direction_available(info, direction):
                    continue

                raw_name = str(info.get("name", "")).strip()
                default_name = "Input Device" if direction == "input" else "Output Device"
                device_id = raw_name or f"{default_name} {index}"
                if device_id in seen_ids:
                    device_id = f"{device_id} [{index}]"
                seen_ids.add(device_id)
                devices.append(
                    {
                        "id": device_id,
                        "label": self._format_audio_device_label(raw_name, index, direction),
                        "index": index,
                    }
                )
        except Exception as exc:
            print(f"Audio Device Enumeration Error: {exc}")
            devices = []
        finally:
            try:
                audio.terminate()
            except Exception:
                pass

        return devices

    def _ensure_settings(self, settings):
        if isinstance(settings, Settings):
            return settings
        return self._coerce(settings, strict=False)

    def _coerce(self, raw_settings, strict):
        defaults = self.defaults()
        if not isinstance(raw_settings, Mapping):
            return defaults

        language_code = self._coerce_required_string(
            raw_settings.get("language_code"),
            defaults.language_code,
            strict,
            "language_code",
        )
        gemini_model = self._coerce_required_string(
            raw_settings.get("gemini_model"),
            defaults.gemini_model,
            strict,
            "gemini_model",
        )
        wake_words = self._coerce_wake_words(raw_settings.get("wake_words"), defaults.wake_words, strict)
        theme = self._coerce_choice(raw_settings.get("theme"), defaults.theme, THEME_OPTIONS, strict, "theme")
        animation_speed = self._coerce_choice(
            raw_settings.get("animation_speed"),
            defaults.animation_speed,
            ANIMATION_SPEED_OPTIONS,
            strict,
            "animation_speed",
        )
        microphone_device_id = self._coerce_audio_device(
            raw_settings.get("microphone_device_id"),
            defaults.microphone_device_id,
            strict,
            "microphone_device_id",
            self.list_input_audio_devices,
        )
        output_audio_device_id = self._coerce_audio_device(
            raw_settings.get("output_audio_device_id"),
            defaults.output_audio_device_id,
            strict,
            "output_audio_device_id",
            self.list_output_audio_devices,
        )
        mcp_server_command = self._coerce_optional_string(
            raw_settings.get("mcp_server_command"),
            defaults.mcp_server_command,
        )
        mcp_default_tool = self._coerce_optional_string(
            raw_settings.get("mcp_default_tool"),
            defaults.mcp_default_tool,
        )
        mcp_enabled = self._coerce_bool(raw_settings.get("mcp_enabled"), defaults.mcp_enabled)

        if strict:
            raise RuntimeError("Strict coercion should use _validate().")

        return Settings(
            language_code=language_code,
            wake_words=wake_words,
            gemini_model=gemini_model,
            theme=theme,
            animation_speed=animation_speed,
            microphone_device_id=microphone_device_id,
            output_audio_device_id=output_audio_device_id,
            mcp_server_command=mcp_server_command,
            mcp_default_tool=mcp_default_tool,
            mcp_enabled=mcp_enabled,
        )

    def _validate(self, raw_settings):
        defaults = self.defaults()
        errors = {}
        if not isinstance(raw_settings, Mapping):
            raw_settings = {}

        language_code = self._coerce_required_string(
            raw_settings.get("language_code"),
            defaults.language_code,
            True,
            "language_code",
            errors,
        )
        gemini_model = self._coerce_required_string(
            raw_settings.get("gemini_model"),
            defaults.gemini_model,
            True,
            "gemini_model",
            errors,
        )
        wake_words = self._coerce_wake_words(raw_settings.get("wake_words"), defaults.wake_words, True, errors)
        theme = self._coerce_choice(raw_settings.get("theme"), defaults.theme, THEME_OPTIONS, True, "theme", errors)
        animation_speed = self._coerce_choice(
            raw_settings.get("animation_speed"),
            defaults.animation_speed,
            ANIMATION_SPEED_OPTIONS,
            True,
            "animation_speed",
            errors,
        )
        microphone_device_id = self._coerce_audio_device(
            raw_settings.get("microphone_device_id"),
            defaults.microphone_device_id,
            True,
            "microphone_device_id",
            self.list_input_audio_devices,
            errors,
        )
        output_audio_device_id = self._coerce_audio_device(
            raw_settings.get("output_audio_device_id"),
            defaults.output_audio_device_id,
            True,
            "output_audio_device_id",
            self.list_output_audio_devices,
            errors,
        )
        mcp_server_command = self._coerce_optional_string(
            raw_settings.get("mcp_server_command"),
            defaults.mcp_server_command,
        )
        mcp_default_tool = self._coerce_optional_string(
            raw_settings.get("mcp_default_tool"),
            defaults.mcp_default_tool,
        )
        mcp_enabled = self._coerce_bool(raw_settings.get("mcp_enabled"), defaults.mcp_enabled)

        if errors:
            return ValidationResult(settings=None, errors=errors)

        return ValidationResult(
            settings=Settings(
                language_code=language_code,
                wake_words=wake_words,
                gemini_model=gemini_model,
                theme=theme,
                animation_speed=animation_speed,
                microphone_device_id=microphone_device_id,
                output_audio_device_id=output_audio_device_id,
                mcp_server_command=mcp_server_command,
                mcp_default_tool=mcp_default_tool,
                mcp_enabled=mcp_enabled,
            ),
            errors={},
        )

    def _coerce_required_string(self, value, default, strict, field_name, errors=None):
        normalized = str(value).strip() if value is not None else ""
        if field_name == "language_code" and normalized and not LANGUAGE_CODE_PATTERN.fullmatch(normalized):
            normalized = ""
        if field_name == "gemini_model" and normalized and not MODEL_NAME_PATTERN.fullmatch(normalized):
            normalized = ""
        if normalized:
            return normalized
        if strict:
            errors[field_name] = "This field is required."
        return default

    def _coerce_wake_words(self, value, default, strict, errors=None):
        wake_words = _normalize_wake_words(value)
        if wake_words:
            return wake_words
        if strict:
            errors["wake_words"] = "Enter at least one wake word."
        return list(default)

    def _coerce_optional_string(self, value, default):
        if value is None:
            return str(default)
        return str(value).strip()

    def _coerce_bool(self, value, default):
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {"1", "true", "yes", "on"}:
                return True
            if normalized in {"0", "false", "no", "off"}:
                return False
        if value is None:
            return bool(default)
        return bool(value)

    def _coerce_choice(self, value, default, choices, strict, field_name, errors=None):
        normalized = str(value).strip()
        if normalized in choices:
            return normalized
        if strict:
            errors[field_name] = "Choose one of the available options."
        return default

    def _coerce_audio_device(self, value, default, strict, field_name, list_devices, errors=None):
        normalized = str(value).strip() if value is not None else ""
        if not normalized:
            return ""

        available_ids = {device["id"] for device in list_devices()}
        if not strict or normalized in available_ids:
            return normalized

        if field_name == "microphone_device_id":
            errors[field_name] = "Choose one of the available input audio devices."
        else:
            errors[field_name] = "Choose one of the available output audio devices."
        return default

    def _is_device_direction_available(self, info, direction):
        channel_key = "maxInputChannels" if direction == "input" else "maxOutputChannels"
        return int(info.get(channel_key, 0)) > 0

    def _format_audio_device_label(self, raw_name, index, direction):
        cleaned = " ".join(str(raw_name).split()).strip(" ,")
        if not cleaned:
            prefix = "Input Device" if direction == "input" else "Output Device"
            return f"{prefix} {index}"
        return cleaned


def get_settings_service():
    return SettingsService()


def validate_settings(raw_settings):
    return get_settings_service()._ensure_settings(raw_settings).to_dict()


def validate_settings_input(raw_settings):
    return get_settings_service().validate(raw_settings)


def load_settings():
    return get_settings_service().load().to_dict()


def load_gemini_api_key():
    return get_settings_service().load_gemini_api_key()


def save_gemini_api_key(api_key):
    return get_settings_service().save_gemini_api_key(api_key)


def save_settings(settings):
    return get_settings_service().save(settings).to_dict()


def apply_settings(settings):
    return get_settings_service().apply(settings).to_dict()
