import os

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# API and model configuration
GOOGLE_API_KEY = os.getenv("GEMINI_KEY")
MODEL_NAME = "gemini-flash-latest"

# Runtime-configurable settings
WAKE_WORDS = ["locus", "local", "locust", "focus"]
LANG_CODE = "en-US"
THEME = "light"
ANIMATION_SPEED = "normal"

CONNECTED_DEVICES = ["Smart Bulb - Living Room", "Smart Plug - Kitchen"]

CHROME_PROFILES = {
    "profile_anton": "Profile 2",
    "profile_mrclean": "Profile 1",
    "profile_default": "Default",
}

DEFAULT_SETTINGS = {
    "language_code": LANG_CODE,
    "wake_words": list(WAKE_WORDS),
    "gemini_model": MODEL_NAME,
    "theme": THEME,
    "animation_speed": ANIMATION_SPEED,
}

ASSETS_DIR = os.path.join(BASE_DIR, "assets")
DATA_DIR = os.path.join(BASE_DIR, "data")
MODEL_DATA_PATH = os.path.join(DATA_DIR, "data.pth")
SETTINGS_PATH = os.path.join(DATA_DIR, "settings.json")
INTENTS_PATH = os.path.join(BASE_DIR, "src", "brain", "intents.json")
