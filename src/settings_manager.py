import json
import os

import src.config as config


ALLOWED_THEMES = {"light", "dark", "colorful"}
ALLOWED_ANIMATION_SPEEDS = {"slow", "normal", "fast"}


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

    return wake_words or list(config.DEFAULT_SETTINGS["wake_words"])


def validate_settings(raw_settings):
    settings = dict(config.DEFAULT_SETTINGS)
    if isinstance(raw_settings, dict):
        settings.update(raw_settings)

    language_code = str(settings.get("language_code", "")).strip() or config.DEFAULT_SETTINGS["language_code"]
    gemini_model = str(settings.get("gemini_model", "")).strip() or config.DEFAULT_SETTINGS["gemini_model"]

    theme = settings.get("theme", config.DEFAULT_SETTINGS["theme"])
    if theme not in ALLOWED_THEMES:
        theme = config.DEFAULT_SETTINGS["theme"]

    animation_speed = settings.get("animation_speed", config.DEFAULT_SETTINGS["animation_speed"])
    if animation_speed not in ALLOWED_ANIMATION_SPEEDS:
        animation_speed = config.DEFAULT_SETTINGS["animation_speed"]

    return {
        "language_code": language_code,
        "wake_words": _normalize_wake_words(settings.get("wake_words")),
        "gemini_model": gemini_model,
        "theme": theme,
        "animation_speed": animation_speed,
    }


def load_settings():
    if not os.path.exists(config.SETTINGS_PATH):
        return dict(config.DEFAULT_SETTINGS)

    try:
        with open(config.SETTINGS_PATH, "r", encoding="utf-8") as file_handle:
            return validate_settings(json.load(file_handle))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"Settings Load Error: {exc}")
        return dict(config.DEFAULT_SETTINGS)


def save_settings(settings):
    validated = validate_settings(settings)
    os.makedirs(os.path.dirname(config.SETTINGS_PATH), exist_ok=True)
    with open(config.SETTINGS_PATH, "w", encoding="utf-8") as file_handle:
        json.dump(validated, file_handle, indent=2)
    return validated


def apply_settings(settings):
    validated = validate_settings(settings)
    config.LANG_CODE = validated["language_code"]
    config.WAKE_WORDS = list(validated["wake_words"])
    config.MODEL_NAME = validated["gemini_model"]
    config.THEME = validated["theme"]
    config.ANIMATION_SPEED = validated["animation_speed"]
    return validated
