import os
import shutil
import subprocess
from dataclasses import dataclass
from functools import lru_cache

import google.generativeai as genai

import src.config as config
from src.mcp_client import MCPError, call_mcp_tool


GEMINI_PROMPT_PREFIX = (
    "You are a funny, slightly sarcastic cat assistant named Locus. "
    "You like memes and snacks. Keep answers short and natural. "
    "If it is a greeting, answer briefly like a lazy cat."
)
MAX_GEMINI_INPUT_CHARS = 1500

gemini = None


@dataclass(frozen=True)
class GeminiValidationResult:
    is_valid: bool
    key_error: str = ""
    model_error: str = ""


def _normalize_model_name(model_name):
    normalized = str(model_name or "").strip()
    if normalized.startswith("models/"):
        return normalized
    return f"models/{normalized}"


def validate_gemini_configuration(api_key, model_name):
    normalized_key = str(api_key or "").strip()
    normalized_model = str(model_name or "").strip()

    if not normalized_key:
        return GeminiValidationResult(is_valid=False, key_error="This field is required.")
    if not normalized_model:
        return GeminiValidationResult(is_valid=False, model_error="This field is required.")

    try:
        genai.configure(api_key=normalized_key)
        next(iter(genai.list_models(page_size=1)), None)
    except Exception as exc:
        return GeminiValidationResult(
            is_valid=False,
            key_error=f"Gemini API key validation failed: {exc}",
        )

    try:
        genai.get_model(_normalize_model_name(normalized_model))
    except Exception as exc:
        return GeminiValidationResult(
            is_valid=False,
            model_error=f"Gemini model validation failed: {exc}",
        )

    return GeminiValidationResult(is_valid=True)


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


def _extract_gemini_text(response):
    text = getattr(response, "text", None)
    if text:
        return text.strip()

    candidates = getattr(response, "candidates", None) or []
    for candidate in candidates:
        content = getattr(candidate, "content", None)
        parts = getattr(content, "parts", None) or []
        for part in parts:
            part_text = getattr(part, "text", None)
            if part_text:
                return part_text.strip()
    return ""


def ask_gemini(text):
    """Send a query to Gemini and return a short reply."""
    if not gemini:
        return "Meow... I have no brains right now."

    cleaned_text = " ".join(str(text).split())
    if not cleaned_text:
        return "Meow... say something first."

    try:
        prompt = f"{GEMINI_PROMPT_PREFIX}\nUser said: {cleaned_text[:MAX_GEMINI_INPUT_CHARS]}"
        response = gemini.generate_content(prompt)
        reply = _extract_gemini_text(response)
        return reply or "Meow... Google AI replied with an empty answer."
    except Exception as exc:
        print(f"Gemini Request Error: {exc}")
        return "Meow... Google AI is not answering."


def is_mcp_available():
    return bool(config.MCP_ENABLED and str(config.MCP_SERVER_COMMAND).strip() and str(config.MCP_DEFAULT_TOOL).strip())


def ask_mcp(text=None, tool_name=None, arguments=None):
    selected_tool = str(tool_name or config.MCP_DEFAULT_TOOL or "").strip()
    if not config.MCP_ENABLED:
        return "Meow... MCP is disabled right now."
    if not str(config.MCP_SERVER_COMMAND).strip():
        return "Meow... MCP server command is not configured."
    if not selected_tool:
        return "Meow... MCP tool is not configured."

    payload = dict(arguments or {})
    cleaned_text = " ".join(str(text or "").split()).strip()
    if cleaned_text and "query" not in payload:
        payload["query"] = cleaned_text

    try:
        return call_mcp_tool(config.MCP_SERVER_COMMAND, selected_tool, arguments=payload)
    except MCPError as exc:
        print(f"MCP Request Error: {exc}")
        return f"Meow... MCP failed: {exc}"


@lru_cache(maxsize=1)
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
    for possible_path in possible_paths:
        if os.path.exists(possible_path):
            return possible_path
    return None


def _launch_chrome(profile_dir, url=None):
    chrome_path = find_chrome()
    if not chrome_path:
        return False

    command = [chrome_path, f"--profile-directory={profile_dir}"]
    if url:
        command.append(url)

    try:
        subprocess.Popen(command)
        print(f"LOG: Launching Chrome with profile {profile_dir}")
        return True
    except OSError as exc:
        print(f"Chrome Launch Error: {exc}")
        return False


def execute_command_logic(tag, confidence, active_context):
    """Map a classified intent into a UI/action result."""
    print(f"DEBUG ACTION: Tag={tag}, Conf={confidence:.2f}, Context={active_context}")

    if active_context:
        if tag in config.CHROME_PROFILES:
            profile_dir = config.CHROME_PROFILES[tag]
            url = "https://www.youtube.com" if active_context == "waiting_for_profile_youtube" else None
            return ("success", None) if _launch_chrome(profile_dir, url=url) else ("error", None)

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

    if tag == "project_status" and confidence > 0.60:
        return "mcp_status_request", None

    if is_mcp_available() and confidence > 0.20:
        return "mcp_request", None

    if confidence > 0.20:
        return "gemini_request", None

    return "unknown", None


reload_gemini_client()
