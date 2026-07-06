import subprocess
import shutil
import os
import google.generativeai as genai
from src.config import GOOGLE_API_KEY, CHROME_PROFILES, MODEL_NAME

# --- Gemini AI Initialization ---
gemini = None
if GOOGLE_API_KEY:
    try:
        genai.configure(api_key=GOOGLE_API_KEY)
        gemini = genai.GenerativeModel(MODEL_NAME)
    except Exception as e:
        print(f"Gemini Init Error: {e}")

def ask_gemini(text):
    """Sends a query to the AI and returns a text response."""
    if not gemini:
        return "Meow... I have no brains (API Key missing)."
    try:
        # --- CHANGE HERE: CAT PERSONALITY ---
        # AI instruction: Be a cat, use a meme-like style, be short and funny.
        prompt = (
            f"You are a funny, slightly sarcastic cat assistant named Locus. "
            f"You like memes and snacks. Keep answers short (1 sentence). "
            f"If it's a greeting, simply say 'Meow?' or something lazy. "
            f"User said: {text}"
        )
        response = gemini.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Gemini Request Error: {e}")
        return "Meow... Connection error to Google AI."

# --- Searching for installed Chrome ---
def find_chrome():
    """Searches for the path to chrome.exe in standard Windows folders."""
    path = shutil.which("chrome") or shutil.which("google-chrome")
    if path: return path
    
    possible_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe")
    ]
    for p in possible_paths:
        if os.path.exists(p): return p
    return None

CHROME_PATH = find_chrome()

# --- Main command logic ---
def execute_command_logic(tag, confidence, active_context):
    """
    Decides on action based on the tag from the neural network.
    Returns: (action_name, new_context)
    """
    print(f"DEBUG ACTION: Tag={tag}, Conf={confidence:.2f}, Context={active_context}")

    # 1. CONTEXT HANDLING (If waiting for profile selection)
    if active_context:
        if tag in CHROME_PROFILES:
            profile_dir = CHROME_PROFILES[tag]
            
            url = None
            if active_context == "waiting_for_profile_youtube":
                url = "https://www.youtube.com"
            
            if CHROME_PATH:
                cmd = [CHROME_PATH, f"--profile-directory={profile_dir}"]
                if url:
                    cmd.append(url)
                
                print(f"LOG: Launching Chrome with profile {profile_dir}")
                subprocess.Popen(cmd)
                return "success", None
            else:
                return "error", None

        if tag == "bye":
            return "bye", None
            
        return "think", active_context

    # 2. "COOL CAT" (State: How are you?)
    if tag == "how_are_you" and confidence > 0.60:
        return "gemini_cool_request", None

    # 3. OPEN YOUTUBE
    if tag == "open_youtube" and confidence > 0.60:
        return "ask_profile_yt", "waiting_for_profile_youtube"

    # 4. OPEN BROWSER
    if tag == "open_browser" and confidence > 0.60:
        return "ask_profile_chrome", "waiting_for_profile_browser"

    # 5. FAREWELL
    if tag == "bye" and confidence > 0.60:
        return "bye", None

    # 6. EVERYTHING ELSE (Including 'greeting') -> GEMINI
    # Now Gemini will respond like a cat, not a robot.
    if confidence > 0.20:
        return "gemini_request", None
    
    return "unknown", None
