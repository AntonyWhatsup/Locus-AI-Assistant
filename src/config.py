import os
from dotenv import load_dotenv

load_dotenv()

# --- API and Model Configuration ---
GOOGLE_API_KEY = os.getenv('GEMINI_KEY')
MODEL_NAME = 'gemini-flash-latest' 

# Wake words for assistant activation (робимо списком, який можна динамічно змінювати)
WAKE_WORDS = ["locus", "local", "locust", "focus"]
LANG_CODE = "en-US"

# Connected devices (додатковий параметр для підключення пристроїв)
CONNECTED_DEVICES = ["Smart Bulb - Living Room", "Smart Plug - Kitchen"]

# Chrome browser profiles
# (Verified: Anton -> Profile 2, Mr Clean -> Profile 1)
CHROME_PROFILES = {
    "profile_anton": "Profile 2",   
    "profile_mrclean": "Profile 1", 
    "profile_default": "Default"    
}

# --- File Paths ---
# BASE_DIR should point to the root directory, which is one level up from src/
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')
MODEL_DATA_PATH = os.path.join(BASE_DIR, "data", "data.pth")
INTENTS_PATH = os.path.join(BASE_DIR, "src", "brain", "intents.json")
