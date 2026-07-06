import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('GEMINI_KEY')

print("--- DIAGNOSTICS ---")
try:
    print(f"Library version: {genai.__version__}")
except:
    print("Library version: <too old to show version>")

if not api_key:
    print("ERROR: No key in .env!")
else:
    genai.configure(api_key=api_key)
    print(f"Key found: {api_key[:5]}...{api_key[-5:]}")
    print("\nAvailable models (what your script sees):")
    try:
        found = False
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f" - {m.name}")
                found = True
        if not found:
            print("List is empty (key or region issue).")
    except Exception as e:
        print(f"CRITICAL REQUEST ERROR: {e}")
