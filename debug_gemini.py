import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('GEMINI_KEY')

print("--- ДІАГНОСТИКА ---")
try:
    print(f"Версія бібліотеки: {genai.__version__}")
except:
    print("Версія бібліотеки: <надто стара, щоб показати версію>")

if not api_key:
    print("ПОМИЛКА: Немає ключа в .env!")
else:
    genai.configure(api_key=api_key)
    print(f"Ключ знайдено: {api_key[:5]}...{api_key[-5:]}")
    print("\nДоступні моделі (що бачить твій скрипт):")
    try:
        found = False
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f" - {m.name}")
                found = True
        if not found:
            print("Список порожній (проблема з ключем або регіоном).")
    except Exception as e:
        print(f"КРИТИЧНА ПОМИЛКА ЗАПИТУ: {e}")