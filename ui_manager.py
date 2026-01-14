import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os
import random
from config import ASSETS_DIR

class LocusUI:
    def __init__(self, root):
        self.root = root
        self.current_raw_img = None
        self.animation_id = None
        self.is_visualizer_running = False
        
        self.root.title("Locus AI v1.9 - Master")
        self.root.geometry("450x620")
        self.root.config(bg="#f5f5f5")

        # Główny obraz kota (Dodano cursor="hand2" dla efektu klikalności)
        self.image_label = tk.Label(root, bg="#f5f5f5", cursor="hand2")
        self.image_label.pack(pady=20)

        # Pasek głośności (Wizualizator)
        self.volume_bar = ttk.Progressbar(root, length=300, mode='determinate')
        self.volume_bar.pack()

        # Status tekstowy
        self.status_label = tk.Label(root, text="System Ready", font=("Arial", 14, "bold"), bg="#f5f5f5")
        self.status_label.pack(pady=10)

        # Tekst dialogu
        self.user_speech_label = tk.Label(root, text="", wraplength=400, font=("Arial", 10), bg="#f5f5f5")
        self.user_speech_label.pack(pady=5)

    def fade_to_image(self, state):
        """Płynna zmiana obrazu na podstawie stanu (idle, listen, cool, train...)"""
        if self.animation_id: self.root.after_cancel(self.animation_id)
        
        path = os.path.join(ASSETS_DIR, f"cat_{state}.jpg")
        
        if not os.path.exists(path): 
            print(f"UI WARNING: Image not found for state '{state}', using idle.")
            path = os.path.join(ASSETS_DIR, "cat_idle.jpg")
        
        try:
            img_open = Image.open(path).resize((300, 300), Image.Resampling.LANCZOS).convert("RGBA")
        except Exception as e:
            print(f"UI ERROR: Could not open image {path}: {e}")
            return

        if self.current_raw_img is None:
            photo = ImageTk.PhotoImage(img_open)
            self.image_label.config(image=photo); self.image_label.image = photo
            self.current_raw_img = img_open
            return

        # Animacja przejścia (Alpha Blending)
        def step(alpha):
            if alpha > 1.0: 
                self.current_raw_img = img_open
                return
            blended = Image.blend(self.current_raw_img, img_open, alpha)
            photo = ImageTk.PhotoImage(blended)
            self.image_label.config(image=photo); self.image_label.image = photo
            self.animation_id = self.root.after(30, lambda: step(alpha + 0.1))
        step(0.0)

    # --- WIZUALIZATOR DŹWIĘKU ---
    def start_visualizer(self):
        self.is_visualizer_running = True
        def anim():
            if self.is_visualizer_running:
                val = random.randint(10, 85)
                self.volume_bar['value'] = val
                self.root.after(100, anim)
            else:
                self.volume_bar['value'] = 0
        anim()

    def stop_visualizer(self):
        self.is_visualizer_running = False
        self.volume_bar['value'] = 0