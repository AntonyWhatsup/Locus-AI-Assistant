import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
api_key = os.getenv("GEMINI_KEY") or os.getenv("GEMINI_API_KEY")

print("--- DIAGNOSTICS ---")

if not api_key:
    print("ERROR: No key in .env!")
else:
    print(f"Key found: {api_key[:5]}...{api_key[-5:]}")
    print("\nAvailable models (what your script sees):")
    try:
        client = genai.Client(api_key=api_key)
        found = False
        for model in client.models.list():
            print(f" - {model.name}")
            found = True
        if not found:
            print("List is empty (key or region issue).")
    except Exception as e:
        print(f"CRITICAL REQUEST ERROR: {e}")
