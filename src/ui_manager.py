import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import os
import random
from src.config import ASSETS_DIR
import src.config as config

class LocusUI:
    def __init__(self, root):
        self.root = root
        self.current_raw_img = None
        self.animation_id = None
        self.is_visualizer_running = False
        
        self.root.title("Locus AI v1.9 - Master")
        self.root.geometry("450x670")
        self.root.config(bg="#f5f5f5")

        # Main cat image (Added cursor="hand2" for clickability effect)
        self.image_label = tk.Label(root, bg="#f5f5f5", cursor="hand2")
        self.image_label.pack(pady=20)

        # Volume bar (Visualizer)
        self.volume_bar = ttk.Progressbar(root, length=300, mode='determinate')
        self.volume_bar.pack()

        # Status text
        self.status_label = tk.Label(root, text="System Ready", font=("Arial", 14, "bold"), bg="#f5f5f5")
        self.status_label.pack(pady=10)

        # Dialogue text
        self.user_speech_label = tk.Label(root, text="", wraplength=400, font=("Arial", 10), bg="#f5f5f5")
        self.user_speech_label.pack(pady=5)

        # Settings Button
        self.settings_btn = tk.Button(
            root, 
            text="⚙ Налаштування", 
            font=("Arial", 10, "bold"), 
            bg="#e0e0e0", 
            fg="#333333", 
            relief="flat",
            command=self.open_settings_window
        )
        self.settings_btn.pack(pady=15)

    def fade_to_image(self, state):
        """Smooth image change based on state (idle, listen, cool, train...)"""
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
            photo = ImageTk.PhotoImage(