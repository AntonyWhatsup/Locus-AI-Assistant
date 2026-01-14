import os
from dotenv import load_dotenv

load_dotenv()

# --- Konfiguracja API i Modelu ---
GOOGLE_API_KEY = os.getenv('GEMINI_KEY')
MODEL_NAME = 'gemini-flash-latest' 

# Słowa aktywujące asystenta
WAKE_WORDS = ["locus", "local", "locust", "focus"]
LANG_CODE = "en-US"

# Profile przeglądarki Chrome
# (Sprawdzone: Anton -> Profile 2, Mr Clean -> Profile 1)
CHROME_PROFILES = {
    "profile_anton": "Profile 2",   
    "profile_mrclean": "Profile 1", 
    "profile_default": "Default"    
}

# --- Ścieżki do plików ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')
MODEL_DATA_PATH = os.path.join(BASE_DIR, "data.pth")
INTENTS_PATH = os.path.join(BASE_DIR, "intents.json")   