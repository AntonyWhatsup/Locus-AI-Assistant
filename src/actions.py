import os
import shutil
import subprocess

import google.generativeai as genai

import src.config as config


gemini = None


def reload_gemini_client():
    global gemini
    gemini = None

    if not config.GOOGLE_API_KEY:
        return None

    try:
        genai.configure(api_key=config.GOOGLE_API_KEY)
        gemini = genai.GenerativeModel(config.MODEL_NAME)
    except Exception as exc:
        print(f"Gemini Init Error: {exc}")
        gemini = None

    return gemini


def ask_gemini(text):
    """Send a query to Gemini and return a short reply."""
    if not gemini:
        return "Meow... I have no brains right now."

    try:
        prompt = (
            "You are a funny, slightly sarcastic cat assistant named Locus. "
            "You like memes and snacks. Keep answers short and natural. "
            "If it is a greeting, answer briefly like a lazy cat. "
            f"User said: {text}"
        )
        response = gemini.generate_content(prompt)
        return response.text
    except Exception as exc:
        print(f"Gemini Request Error: {exc}")
        return "Meow... Google AI is not answering."


def find_chrome():
    """Search for chrome.exe in standard Windows locations."""
    path = shutil.which("chrome") or shutil.which("google-chrome")
    if path:
        return path

    possible_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe"),
    ]
    for path in possible_paths:
        if os.path.exists(path):
            return path
    return None


CHROME_PATH = find_chrome()


def execute_command_logic(tag, confidence, active_context):
    """Map a classified intent into a UI/action result."""
    print(f"DEBUG ACTION: Tag={tag}, Conf={confidence:.2f}, Context={active_context}")

    if active_context:
        if tag in config.CHROME_PROFILES:
            profile_dir = config.CHROME_PROFILES[tag]
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
            return "error", None

        if tag == "bye":
            return "bye", None

        return "think", active_context

    if tag == "how_are_you" and confidence > 0.60:
        return "gemini_cool_request", None

    if tag == "open_youtube" and confidence > 0.60:
        return "ask_profile_yt", "waiting_for_profile_youtube"

    if tag == "open_browser" and confidence > 0.60:
        return "ask_profile_chrome", "waiting_for_profile_browser"

    if tag == "bye" and confidence > 0.60:
        return "bye", None

    if confidence > 0.20:
        return "gemini_request", None

    return "unknown", None


reload_gemini_client()
