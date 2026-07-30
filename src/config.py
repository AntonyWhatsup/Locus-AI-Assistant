import os

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# API and model configuration
ENV_PATH = os.path.join(BASE_DIR, ".env")
GOOGLE_API_KEY = os.getenv("GEMINI_KEY") or os.getenv("GEMINI_API_KEY")
MODEL_NAME = "gemini-2.5-flash"
GEMINI_TIMEOUT_MS = 15000
CLOUD_WAKE_LISTENER_ENABLED = os.getenv("LOCUS_ENABLE_CLOUD_WAKE_LISTENER") == "1"
GEMINI_FALLBACK_ENABLED = os.getenv("LOCUS_ENABLE_GEMINI_FALLBACK") == "1"
DEBUG_MODE = False
LOCAL_INTENT_CACHE_ENABLED = True
MICROPHONE_SENSITIVITY = 65
AUTO_LISTEN_ON_STARTUP = CLOUD_WAKE_LISTENER_ENABLED
SHOW_LIVE_TRANSCRIPT = True
AI_MODEL = "gemini" if GEMINI_FALLBACK_ENABLED else "local"
TTS_VOICE = ""

# Runtime-configurable settings
WAKE_WORDS = ["locus", "local", "locust", "focus"]
LANG_CODE = "en-US"
THEME = "glass-green"
ANIMATION_SPEED = "normal"
MICROPHONE_DEVICE_ID = ""
OUTPUT_AUDIO_DEVICE_ID = ""
MCP_SERVER_COMMAND = ""
MCP_DEFAULT_TOOL = ""
MCP_ENABLED = False

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
    "microphone_sensitivity": MICROPHONE_SENSITIVITY,
    "auto_listen_on_startup": AUTO_LISTEN_ON_STARTUP,
    "show_live_transcript": SHOW_LIVE_TRANSCRIPT,
    "ai_model": AI_MODEL,
    "tts_voice": TTS_VOICE,
    "debug_mode": DEBUG_MODE,
    "local_intent_cache": LOCAL_INTENT_CACHE_ENABLED,
    "microphone_device_id": MICROPHONE_DEVICE_ID,
    "output_audio_device_id": OUTPUT_AUDIO_DEVICE_ID,
    "mcp_server_command": MCP_SERVER_COMMAND,
    "mcp_default_tool": MCP_DEFAULT_TOOL,
    "mcp_enabled": MCP_ENABLED,
}

ASSETS_DIR = os.path.join(BASE_DIR, "assets")
DATA_DIR = os.path.join(BASE_DIR, "data")
MODEL_DATA_PATH = os.path.join(DATA_DIR, "data.pth")
SETTINGS_PATH = os.path.join(DATA_DIR, "settings.json")
INTENTS_PATH = os.path.join(BASE_DIR, "src", "brain", "intents.json")
