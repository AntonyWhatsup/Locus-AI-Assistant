import tkinter as tk
from tkinter import messagebox
import tkinter.ttk as ttk
import speech_recognition as sr
import threading
import torch
import json
import os
import time
import random
import subprocess # Для запуску Chrome з параметрами
from PIL import Image, ImageTk

from model import NeuralNet
from nltk_utils import bag_of_words, tokenize

# --- НАЛАШТУВАННЯ ---
WAKE_WORD = "локус"
is_processing = False
current_raw_img = None
stop_visualizer = False
current_animation_id = None
active_context = None  # Запам'ятовує, про що ми говоримо (контекст)

# ШЛЯХ ДО CHROME (Перевір, чи він такий самий у тебе)
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

# НАЛАШТУВАННЯ ПРОФІЛІВ (Твої дані)
CHROME_PROFILES = {
    "profile_anton": "Profile 2",      # Антон з окулярами
    "profile_mrclean": "Profile 1",    # Клін
    "profile_krykhta": "Default"       # Крихта (Дефолтний)
}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# --- ЗАВАНТАЖЕННЯ МОЗКУ ---
try:
    with open('intents.json', 'r', encoding='utf-8') as f:
        intents = json.load(f)
        
    if not os.path.exists("data.pth"):
        raise FileNotFoundError("Спочатку запусти train.py!")
        
    data = torch.load("data.pth")
    model = NeuralNet(data["input_size"], data["hidden_size"], data["output_size"]).to(device)
    model.load_state_dict(data["model_state"])
    model.eval()
    all_words, tags = data["all_words"], data["tags"]
except Exception as e:
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror("Помилка запуску", f"{e}")
    exit()

# --- АНІМАЦІЇ ---
def cancel_previous_animation():
    global current_animation_id
    if current_animation_id is not None:
        try: root.after_cancel(current_animation_id)
        except: pass
        current_animation_id = None

def fade_to_image(target_state, steps=20):
    cancel_previous_animation()
    global current_raw_img
    target_path = os.path.join(ASSETS_DIR, f"cat_{target_state}.jpg")
    
    if not os.path.exists(target_path): return
    new_img = Image.open(target_path).resize((300, 300), Image.Resampling.LANCZOS).convert("RGBA")
    
    if current_raw_img is None:
        current_raw_img = new_img
        photo = ImageTk.PhotoImage(new_img)
        image_label.config(image=photo); image_label.image = photo
        return

    def animate_step(alpha):
        global current_raw_img, current_animation_id
        if alpha > 1.0: current_raw_img = new_img; return
        blended = Image.blend(current_raw_img, new_img, alpha)
        photo = ImageTk.PhotoImage(blended)
        image_label.config(image=photo); image_label.image = photo
        current_animation_id = root.after(30, lambda: animate_step(alpha + 0.1))
    animate_step(0.0)

def type_text(label, text, delay=20):
    label.config(text="") 
    def next_char(i):
        if i <= len(text):
            label.config(text=text[:i])
            root.after(delay, lambda: next_char(i + 1))
    next_char(0)

def start_mic_visualizer():
    global stop_visualizer; stop_visualizer = False
    def animate_bar():
        if stop_visualizer: volume_bar['value'] = 0; return
        volume_bar['value'] = random.randint(10, 90)
        root.after(100, animate_bar)
    animate_bar()

def stop_mic_visualizer_func(): global stop_visualizer; stop_visualizer = True; volume_bar['value'] = 0

# --- ФУНКЦІЯ ЗАПУСКУ CHROME ---
def open_chrome_profile(profile_folder):
    try:
        # Запускаємо Chrome із вказаним профілем
        subprocess.Popen([CHROME_PATH, "https://www.youtube.com", f"--profile-directory={profile_folder}"])
        return True
    except Exception as e:
        print(f"Помилка запуску Chrome: {e}")
        return False

# --- ЛОГІКА ВИКОНАННЯ ---
def execute_command(tag):
    """
    Виконує дію на основі тегу, який повернула нейромережа.
    """
    print(f"DEBUG: Виконую команду для тегу -> {tag}") # Для відладки
    
    # --- 1. ВІДКРИТТЯ YOUTUBE ---
    if tag == "open_youtube":
        update_status("Відкриваю YouTube...")
        # Перевіряємо, чи є Chrome
        if not os.path.exists(CHROME_PATH):
            messagebox.showerror("Помилка", "Chrome не знайдено! Перевір шлях у коді.")
            return

        # Запускаємо YouTube (можна додати профіль за замовчуванням, якщо треба)
        subprocess.Popen([CHROME_PATH, "https://www.youtube.com"])

    # --- 2. ВІДКРИТТЯ БРАУЗЕРА (GOOGLE) ---
    elif tag == "open_browser":
        update_status("Відкриваю Google...")
        if os.path.exists(CHROME_PATH):
            subprocess.Popen([CHROME_PATH, "https://google.com"])
        else:
            messagebox.showerror("Помилка", "Chrome не знайдено!")

    # --- 3. ЗМІНА ПРОФІЛЮ ---
    # Перевіряємо, чи тег починається з "profile_"
    elif tag.startswith("profile_"):
        # Отримуємо ім'я профілю з тегу (наприклад, "profile_anton")
        if tag in CHROME_PROFILES:
            profile_name = CHROME_PROFILES[tag] # "Profile 2"
            update_status(f"Запускаю профіль: {tag.split('_')[1]}...")
            
            if os.path.exists(CHROME_PATH):
                # Аргумент --profile-directory запускає конкретного юзера
                subprocess.Popen([CHROME_PATH, f"--profile-directory={profile_name}"])
            else:
                messagebox.showerror("Помилка", "Chrome не знайдено!")
        else:
            update_status("Профіль не налаштовано в коді.")

    # --- 4. ПРИВІТАННЯ / ПРОЩАННЯ ---
    elif tag == "greeting":
        update_status("Привіт! Чим можу допомогти?")
    
    elif tag == "bye":
        update_status("До зустрічі!")
        root.after(2000, root.destroy) # Закрити програму через 2 сек

    # --- 5. ЯКЩО НЕЗРОЗУМІЛО ---
    else:
        update_status("Команда розпізнана, але дія не прописана.")

# --- ОБРОБКА ПРОЦЕСУ ---
def listen_and_process():
    global is_processing
    is_processing = True
    
    r = sr.Recognizer()
    with sr.Microphone() as source:
        fade_to_image("listen")
        
        # Підказка в залежності від контексту
        if active_context == "waiting_for_youtube_profile":
            status_label.config(text="Назви акаунт...", fg="#e84393")
        else:
            status_label.config(text="Слухаю...", fg="#d63031")
            
        user_speech_label.config(text="")
        threading.Thread(target=start_mic_visualizer).start()
        root.update()
        
        try:
            audio = r.listen(source, timeout=5, phrase_time_limit=5)
            stop_mic_visualizer_func()
            
            fade_to_image("think") 
            status_label.config(text="Аналізую...", fg="#6c5ce7")
            root.update()
            
            text_input = r.recognize_google(audio, language="uk-UA") 
            type_text(user_speech_label, f"Ви: \"{text_input}\"")
            time.sleep(0.5) 
            
            # Нейромережа
            sentence = tokenize(text_input)
            X = bag_of_words(sentence, all_words)
            X = torch.from_numpy(X.reshape(1, X.shape[0])).to(device)
            
            output = model(X)
            _, predicted = torch.max(output, dim=1)
            tag = tags[predicted.item()]
            probs = torch.softmax(output, dim=1)
            prob = probs[0][predicted.item()]
            
            if prob.item() < 0.60: # Знижений поріг для імен
                tag = "unknown"

            res_state = execute_command(tag, text_input, status_label)
            
            # Якщо Locus задав питання, він сам починає слухати знову через 1.5 сек
            if res_state == "think" and active_context is not None:
                fade_to_image("think")
                root.after(1500, lambda: threading.Thread(target=listen_and_process).start())
            else:
                fade_to_image(res_state)
            
        except Exception as e:
            stop_mic_visualizer_func()
            if active_context: # Якщо чекали відповідь, але тиша - чекаємо далі
                status_label.config(text="Чекаю вибору...", fg="orange")
                fade_to_image("think")
            else:
                status_label.config(text="...", fg="gray")
                fade_to_image("idle")
            print(e)
            
    if active_context is None:
        time.sleep(3.5)
        fade_to_image("idle")
        status_label.config(text="Скажи 'Локус'", fg="black")
    
    is_processing = False

# --- ФОНОВИЙ ПОТІК ---
def background_listener():
    r = sr.Recognizer(); m = sr.Microphone()
    with m as source: r.adjust_for_ambient_noise(source, duration=1)
    while True:
        if not is_processing:
            with m as source:
                try:
                    audio = r.listen(source, phrase_time_limit=2)
                    text = r.recognize_google(audio, language="uk-UA").lower()
                    if WAKE_WORD in text: root.after(0, lambda: threading.Thread(target=listen_and_process).start())
                except: pass
        time.sleep(0.1)

# --- GUI ---
root = tk.Tk()
root.title("Locus AI v0.4.0 - Context Edition")
root.geometry("450x620")
root.config(bg="#f5f5f5")

image_label = tk.Label(root, bg="#f5f5f5", cursor="hand2")
image_label.pack(pady=20)
image_label.bind("<Button-1>", lambda e: threading.Thread(target=listen_and_process).start() if not is_processing else None)

style = ttk.Style(); style.theme_use('default'); style.configure("TProgressbar", thickness=10, background='#0984e3')
volume_bar = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate", style="TProgressbar")
volume_bar.pack(pady=5)

status_label = tk.Label(root, text="Завантаження...", font=("Arial", 14, "bold"), bg="#f5f5f5")
status_label.pack(pady=5)
user_speech_label = tk.Label(root, text="", font=("Arial", 12, "italic"), fg="#636e72", bg="#f5f5f5", wraplength=400)
user_speech_label.pack(pady=10)

threading.Thread(target=background_listener, daemon=True).start()
root.after(100, lambda: fade_to_image("idle"))
root.after(500, lambda: status_label.config(text="Скажи 'Локус'"))

root.mainloop()