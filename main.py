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
import shutil
import subprocess
from datetime import datetime
from PIL import Image, ImageTk

from model import NeuralNet
from nltk_utils import bag_of_words, tokenize

# --- НАЛАШТУВАННЯ ---
WAKE_WORD = "локус"
is_processing = False
current_raw_img = None
stop_visualizer = False
current_animation_id = None
active_context = None 

# --- ПОШУК CHROME ---
def find_chrome():
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

# Профілі
CHROME_PROFILES = {
    "profile_anton": "Profile 2",      
    "profile_mrclean": "Profile 1",    
    "profile_krykhta": "Default"       
}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# --- ЗАВАНТАЖЕННЯ МОДЕЛІ ---
try:
    with open('intents.json', 'r', encoding='utf-8') as f:
        intents = json.load(f)
    if not os.path.exists("data.pth"):
        raise FileNotFoundError("Спочатку запустіть train.py!")
    data = torch.load("data.pth")
    model = NeuralNet(data["input_size"], data["hidden_size"], data["output_size"]).to(device)
    model.load_state_dict(data["model_state"])
    model.eval()
    all_words, tags = data["all_words"], data["tags"]
except Exception as e:
    root = tk.Tk(); root.withdraw()
    messagebox.showerror("Помилка", f"{e}"); exit()

# --- АНІМАЦІЯ ---
def cancel_previous_animation():
    global current_animation_id
    if current_animation_id is not None:
        try: root.after_cancel(current_animation_id)
        except: pass
        current_animation_id = None

def fade_to_image(target_state, steps=20):
    cancel_previous_animation()
    global current_raw_img
    
    # Спробуємо знайти картинку. Якщо "error" немає, беремо "think"
    target_path = os.path.join(ASSETS_DIR, f"cat_{target_state}.jpg")
    if not os.path.exists(target_path):
        if target_state == "error":
            target_path = os.path.join(ASSETS_DIR, "cat_think.jpg") # Запасний варіант
        
    if not os.path.exists(target_path): return # Якщо й запасної немає - вихід

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

# --- ЛОГІКА CHROME ---
def open_chrome_profile(profile_folder, url=None):
    if not CHROME_PATH:
        print("ПОМИЛКА: Не знайдено chrome.exe!")
        return

    cmd = [CHROME_PATH, f"--profile-directory={profile_folder}"]
    if url: cmd.append(url)

    try:
        subprocess.Popen(cmd)
    except Exception as e:
        print(f"ERROR: {e}")

# --- ВИКОНАННЯ ---
# Додали параметр confidence (впевненість), щоб не закривати прогу випадково
def execute_command(tag, text, status_label, confidence=1.0):
    global active_context

    # Якщо тег невідомий - зразу помилка
    if tag == "unknown":
        status_label.config(text="Я не зрозумів...", fg="#e17055")
        return "error"

    # 1. ОБРОБКА ВІДПОВІДІ
    if active_context in ["waiting_for_profile_youtube", "waiting_for_profile_browser"]:
        if tag in CHROME_PROFILES:
            profile_folder = CHROME_PROFILES[tag]
            display_name = tag.split('_')[-1].capitalize()
            status_label.config(text=f"Запускаю: {display_name}", fg="#00b894")
            
            if active_context == "waiting_for_profile_youtube":
                open_chrome_profile(profile_folder, "https://www.youtube.com")
            else:
                open_chrome_profile(profile_folder, None)
            
            active_context = None 
            return "success"
        elif tag == "bye":
            active_context = None
            status_label.config(text="Скасовано.", fg="#636e72")
            return "idle"
        else:
            status_label.config(text="Антон, Клін чи Крихта?", fg="#e17055")
            return "think"

    # 2. КОМАНДИ
    if tag == "open_youtube":
        status_label.config(text="Який акаунт для Ютубу?", fg="#0984e3")
        type_text(user_speech_label, "Locus: Оберіть профіль...")
        active_context = "waiting_for_profile_youtube"
        return "think" 

    if tag == "open_browser":
        status_label.config(text="Який акаунт для Хрому?", fg="#0984e3")
        type_text(user_speech_label, "Locus: Оберіть профіль...")
        active_context = "waiting_for_profile_browser"
        return "think"

    if tag == "create_file":
        active_context = None 
        filename = "LocusNote"
        words = text.split()
        search_markers = ["назвою", "named", "ім'ям", "файл"]
        for m in search_markers:
            if m in words and words.index(m) + 1 < len(words):
                filename = words[words.index(m)+1]
                break
        timestamp = datetime.now().strftime("%H-%M")
        filename = f"{filename}_{timestamp}.txt"
        desktop = os.path.join(os.environ['USERPROFILE'], 'Desktop')
        path = os.path.join(desktop, filename)
        try:
            with open(path, "w", encoding='utf-8') as f:
                f.write(f"Створено Locus AI.\nCmd: {text}")
            status_label.config(text=f"Створено: {filename}", fg="#00b894")
            return "success"
        except Exception as e:
            print(e); return "error"

    elif tag == "greeting":
        status_label.config(text="Привіт! Слухаю.", fg="#0984e3")
        return "success"
        
    elif tag == "bye":
        # !!! ЗАХИСТ ВІД ВИПАДКОВОГО ЗАКРИТТЯ !!!
        if confidence < 0.8:
            # Якщо бот не дуже впевнений, що ви сказали "пока", він не вимкнеться
            status_label.config(text="Ви сказали 'бувай'?", fg="#e17055")
            return "error"
            
        status_label.config(text="До побачення!", fg="#636e72")
        root.after(2000, root.quit)
        return "success"

    # Якщо дійшли сюди - тег є, але він не оброблений (на всяк випадок)
    status_label.config(text="Не зрозумів...", fg="#e17055")
    return "error"

# --- ОБРОБКА ГОЛОСУ ---
def listen_and_process():
    global is_processing
    is_processing = True
    r = sr.Recognizer()
    with sr.Microphone() as source:
        fade_to_image("listen")
        if active_context:
            status_label.config(text="Назви акаунт...", fg="#e84393")
        else:
            status_label.config(text="Слухаю...", fg="#d63031")
        user_speech_label.config(text=""); threading.Thread(target=start_mic_visualizer).start()
        root.update()
        
        try:
            # Слухаємо до 15 секунд
            audio = r.listen(source, timeout=5, phrase_time_limit=15)
            stop_mic_visualizer_func()
            fade_to_image("think") 
            status_label.config(text="Аналізую...", fg="#6c5ce7")
            root.update()
            
            text_input = r.recognize_google(audio, language="uk-UA") 
            type_text(user_speech_label, f"Ви: \"{text_input}\"")
            time.sleep(0.5) 
            
            # NEURAL NET
            sentence = tokenize(text_input)
            X = bag_of_words(sentence, all_words)
            X = torch.from_numpy(X.reshape(1, X.shape[0])).to(device)
            output = model(X)
            _, predicted = torch.max(output, dim=1)
            tag = tags[predicted.item()]
            probs = torch.softmax(output, dim=1)
            prob = probs[0][predicted.item()]
            
            print(f"User said: {text_input}")
            print(f"Predicted: {tag} ({prob.item():.4f})")
            
            # Поріг 0.45
            if prob.item() < 0.45: tag = "unknown"

            # Передаємо prob.item() у функцію виконання
            res_state = execute_command(tag, text_input, status_label, prob.item())
            
            if res_state == "think" and active_context is not None:
                fade_to_image("think")
                root.after(1500, lambda: threading.Thread(target=listen_and_process).start())
            else:
                fade_to_image(res_state)

        except sr.UnknownValueError:
            # Якщо гугл не розібрав слів взагалі
            stop_mic_visualizer_func()
            status_label.config(text="Не розчув...", fg="orange")
            fade_to_image("error") # Покаже cat_think.jpg якщо немає error
            
        except Exception as e:
            stop_mic_visualizer_func()
            status_label.config(text="Помилка", fg="red")
            if active_context: fade_to_image("think")
            else: fade_to_image("idle")
            print(f"Log: {e}")
            
    if active_context is None:
        time.sleep(3.5); fade_to_image("idle"); status_label.config(text="Скажи 'Локус'", fg="black")
    is_processing = False

# --- WAKE WORD ---
def background_listener():
    r = sr.Recognizer(); m = sr.Microphone()
    with m as source: r.adjust_for_ambient_noise(source, duration=1)
    while True:
        if not is_processing:
            with m as source:
                try:
                    audio = r.listen(source, phrase_time_limit=3)
                    text = r.recognize_google(audio, language="uk-UA").lower()
                    if WAKE_WORD in text: root.after(0, lambda: threading.Thread(target=listen_and_process).start())
                except: pass
        time.sleep(0.1)

# --- GUI START ---
root = tk.Tk()
root.title("Locus AI v0.9.5 - Safe Mode")
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