import os
import tkinter as tk
from tkinter import messagebox, ttk

from PIL import Image, ImageTk

from src.actions import reload_gemini_client
from src.config import ASSETS_DIR
from src.settings_manager import apply_settings, load_settings, save_settings
import src.config as config


THEMES = {
    "light": {
        "root_bg": "#f4f7fb",
        "panel": "#ffffff",
        "panel_alt": "#eef3f9",
        "border": "#d9e2ef",
        "title": "#1f2937",
        "text": "#334155",
        "muted": "#64748b",
        "accent": "#2563eb",
        "accent_soft": "#dbeafe",
        "accent_alt": "#38bdf8",
        "success": "#15803d",
        "warning": "#d97706",
        "danger": "#dc2626",
        "button_bg": "#2563eb",
        "button_fg": "#ffffff",
        "secondary_bg": "#e2e8f0",
        "secondary_fg": "#334155",
        "chip_bg": "#eff6ff",
        "chip_fg": "#1d4ed8",
        "bar_off": "#dbe4f0",
        "bar_on": "#2563eb",
    },
    "dark": {
        "root_bg": "#0f172a",
        "panel": "#111827",
        "panel_alt": "#1f2937",
        "border": "#334155",
        "title": "#f8fafc",
        "text": "#cbd5e1",
        "muted": "#94a3b8",
        "accent": "#60a5fa",
        "accent_soft": "#1e3a8a",
        "accent_alt": "#22d3ee",
        "success": "#4ade80",
        "warning": "#f59e0b",
        "danger": "#f87171",
        "button_bg": "#60a5fa",
        "button_fg": "#0f172a",
        "secondary_bg": "#1e293b",
        "secondary_fg": "#e2e8f0",
        "chip_bg": "#1e3a8a",
        "chip_fg": "#bfdbfe",
        "bar_off": "#334155",
        "bar_on": "#60a5fa",
    },
    "colorful": {
        "root_bg": "#fff7ed",
        "panel": "#ffffff",
        "panel_alt": "#fff1f2",
        "border": "#fecdd3",
        "title": "#3b0764",
        "text": "#5b365f",
        "muted": "#7c3f58",
        "accent": "#ec4899",
        "accent_soft": "#fce7f3",
        "accent_alt": "#f97316",
        "success": "#16a34a",
        "warning": "#ea580c",
        "danger": "#dc2626",
        "button_bg": "#ec4899",
        "button_fg": "#ffffff",
        "secondary_bg": "#fde68a",
        "secondary_fg": "#7c2d12",
        "chip_bg": "#ede9fe",
        "chip_fg": "#7c3aed",
        "bar_off": "#fbcfe8",
        "bar_on": "#ec4899",
    },
}

ANIMATION_SPEEDS = {
    "slow": {"delay": 80, "smoothing": 0.15},
    "normal": {"delay": 55, "smoothing": 0.22},
    "fast": {"delay": 35, "smoothing": 0.30},
}

THEME_CHOICES = {
    "light": ("Light", "Clean and minimal"),
    "dark": ("Dark", "Low-light focused"),
    "colorful": ("Colorful", "Modern and playful"),
}

STATUS_TONES = {
    "idle": "muted",
    "listening": "accent",
    "thinking": "accent_alt",
    "prompt": "warning",
    "success": "success",
    "error": "danger",
}


class LocusUI:
    def __init__(self, root):
        self.root = root
        self.current_raw_img = None
        self.animation_id = None
        self.manual_action = None
        self.settings_window = None
        self.current_theme_name = config.THEME
        self.theme = THEMES.get(self.current_theme_name, THEMES["light"])

        self.mic_state = "idle"
        self.mic_level = 0.0
        self.smoothed_level = 0.0
        self.bar_loop_id = None
        self.bar_tick = 0

        self.root.title("Locus AI")
        self.root.geometry("560x840")
        self.root.minsize(540, 800)

        self._configure_styles()
        self._build_layout()
        self.apply_theme()
        self.fade_to_image("idle")
        self.set_status("Say 'Locus'", "idle", "Left-click the cat or press Listen.")
        self.set_transcript(
            user_text="Waiting for your command.",
            locus_text="I am ready. Say the wake word or start listening manually.",
        )
        self._start_bar_loop()

    def _configure_styles(self):
        self.ttk_style = ttk.Style()
        try:
            self.ttk_style.theme_use("clam")
        except tk.TclError:
            pass

    def _build_layout(self):
        self.main_frame = tk.Frame(self.root, bd=0, highlightthickness=0)
        self.main_frame.pack(fill="both", expand=True, padx=18, pady=18)

        self.header_frame = tk.Frame(self.main_frame, bd=0, highlightthickness=0)
        self.header_frame.pack(fill="x", pady=(0, 14))

        self.title_label = tk.Label(
            self.header_frame,
            text="Locus AI",
            font=("Segoe UI Semibold", 24),
            anchor="w",
        )
        self.title_label.pack(side="left")

        self.theme_badge = tk.Label(
            self.header_frame,
            text="Light UI",
            font=("Segoe UI", 9, "bold"),
            padx=10,
            pady=6,
        )
        self.theme_badge.pack(side="right")

        self.subtitle_label = tk.Label(
            self.main_frame,
            text="Voice assistant with cat reactions, local intents, and Gemini fallback.",
            font=("Segoe UI", 10),
            anchor="w",
        )
        self.subtitle_label.pack(fill="x", pady=(0, 14))

        self.hero_card = self._create_card(self.main_frame)
        self.hero_card.pack(fill="x", pady=(0, 14))

        self.hero_top = tk.Frame(self.hero_card, bd=0, highlightthickness=0)
        self.hero_top.pack(fill="x", padx=18, pady=(18, 10))

        self.hero_title = tk.Label(
            self.hero_top,
            text="Assistant",
            font=("Segoe UI Semibold", 16),
            anchor="w",
        )
        self.hero_title.pack(side="left")

        self.hero_hint = tk.Label(
            self.hero_top,
            text="Click the cat to wake it",
            font=("Segoe UI", 9, "bold"),
            padx=10,
            pady=4,
        )
        self.hero_hint.pack(side="right")

        self.image_frame = tk.Frame(self.hero_card, bd=0, highlightthickness=0)
        self.image_frame.pack(padx=18, pady=(0, 10))

        self.image_label = tk.Label(self.image_frame, cursor="hand2", bd=0, highlightthickness=0)
        self.image_label.pack()

        self.hero_caption = tk.Label(
            self.hero_card,
            text="Wake words: " + ", ".join(config.WAKE_WORDS),
            font=("Segoe UI", 9),
            anchor="w",
            justify="left",
        )
        self.hero_caption.pack(fill="x", padx=18, pady=(0, 16))

        self.mic_card = self._create_card(self.main_frame)
        self.mic_card.pack(fill="x", pady=(0, 14))

        self.mic_header = tk.Frame(self.mic_card, bd=0, highlightthickness=0)
        self.mic_header.pack(fill="x", padx=18, pady=(18, 6))

        self.status_text = tk.Label(
            self.mic_header,
            text="System Ready",
            font=("Segoe UI Semibold", 16),
            anchor="w",
        )
        self.status_text.pack(side="left")

        self.mic_mode_label = tk.Label(
            self.mic_header,
            text="Idle",
            font=("Segoe UI", 9, "bold"),
            padx=10,
            pady=4,
        )
        self.mic_mode_label.pack(side="right")

        self.status_subtext = tk.Label(
            self.mic_card,
            text="Real microphone level will appear here during listening.",
            font=("Segoe UI", 10),
            anchor="w",
            justify="left",
        )
        self.status_subtext.pack(fill="x", padx=18, pady=(0, 10))

        self.mic_canvas = tk.Canvas(self.mic_card, width=470, height=96, bd=0, highlightthickness=0)
        self.mic_canvas.pack(fill="x", padx=18, pady=(0, 16))

        self.transcript_card = self._create_card(self.main_frame)
        self.transcript_card.pack(fill="x", pady=(0, 14))

        self.transcript_title = tk.Label(
            self.transcript_card,
            text="Conversation",
            font=("Segoe UI Semibold", 16),
            anchor="w",
        )
        self.transcript_title.pack(fill="x", padx=18, pady=(18, 12))

        self.user_card = tk.Frame(self.transcript_card, bd=0, highlightthickness=0)
        self.user_card.pack(fill="x", padx=18, pady=(0, 10))

        self.user_heading = tk.Label(self.user_card, text="You", font=("Segoe UI", 9, "bold"), anchor="w")
        self.user_heading.pack(fill="x", padx=12, pady=(10, 4))

        self.user_text_label = tk.Label(
            self.user_card,
            text="",
            font=("Segoe UI", 11),
            justify="left",
            anchor="w",
            wraplength=450,
        )
        self.user_text_label.pack(fill="x", padx=12, pady=(0, 12))

        self.locus_card = tk.Frame(self.transcript_card, bd=0, highlightthickness=0)
        self.locus_card.pack(fill="x", padx=18, pady=(0, 18))

        self.bot_heading = tk.Label(self.locus_card, text="Locus", font=("Segoe UI", 9, "bold"), anchor="w")
        self.bot_heading.pack(fill="x", padx=12, pady=(10, 4))

        self.locus_text_label = tk.Label(
            self.locus_card,
            text="",
            font=("Segoe UI", 11),
            justify="left",
            anchor="w",
            wraplength=450,
        )
        self.locus_text_label.pack(fill="x", padx=12, pady=(0, 12))

        self.footer_frame = tk.Frame(self.main_frame, bd=0, highlightthickness=0)
        self.footer_frame.pack(fill="x")

        self.listen_btn = tk.Button(
            self.footer_frame,
            text="Listen",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            command=self.trigger_manual_action,
            cursor="hand2",
            padx=18,
            pady=10,
        )
        self.listen_btn.pack(side="left")

        self.settings_btn = tk.Button(
            self.footer_frame,
            text="Settings",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            command=self.open_settings_window,
            cursor="hand2",
            padx=18,
            pady=10,
        )
        self.settings_btn.pack(side="left", padx=(10, 0))

    def _create_card(self, parent):
        return tk.Frame(parent, bd=0, highlightthickness=1)

    def apply_theme(self, theme_name=None):
        if theme_name:
            self.current_theme_name = theme_name
        self.theme = THEMES.get(self.current_theme_name, THEMES["light"])

        self.root.config(bg=self.theme["root_bg"])
        self.main_frame.config(bg=self.theme["root_bg"])
        self.header_frame.config(bg=self.theme["root_bg"])
        self.footer_frame.config(bg=self.theme["root_bg"])
        self.subtitle_label.config(bg=self.theme["root_bg"], fg=self.theme["muted"])
        self.title_label.config(bg=self.theme["root_bg"], fg=self.theme["title"])

        theme_title = THEME_CHOICES.get(self.current_theme_name, ("Light", ""))[0]
        self.theme_badge.config(bg=self.theme["chip_bg"], fg=self.theme["chip_fg"], text=f"{theme_title} UI")

        for widget in (self.hero_card, self.mic_card, self.transcript_card):
            widget.config(bg=self.theme["panel"], highlightbackground=self.theme["border"])

        for widget in (self.hero_top, self.mic_header, self.user_card, self.locus_card):
            widget.config(bg=self.theme["panel_alt"], highlightbackground=self.theme["border"], highlightthickness=1)

        self.hero_title.config(bg=self.theme["panel_alt"], fg=self.theme["title"])
        self.hero_hint.config(bg=self.theme["chip_bg"], fg=self.theme["chip_fg"])
        self.image_frame.config(bg=self.theme["panel"])
        self.image_label.config(bg=self.theme["panel"])
        self.hero_caption.config(bg=self.theme["panel"], fg=self.theme["muted"])

        self.status_text.config(bg=self.theme["panel_alt"], fg=self.theme["title"])
        self.mic_mode_label.config(bg=self.theme["chip_bg"], fg=self.theme["chip_fg"])
        self.status_subtext.config(bg=self.theme["panel"], fg=self.theme["muted"])
        self.mic_canvas.config(bg=self.theme["panel"])

        self.transcript_title.config(bg=self.theme["panel"], fg=self.theme["title"])
        self.user_heading.config(bg=self.theme["panel_alt"], fg=self.theme["muted"])
        self.bot_heading.config(bg=self.theme["panel_alt"], fg=self.theme["muted"])
        self.user_text_label.config(bg=self.theme["panel_alt"], fg=self.theme["text"])
        self.locus_text_label.config(bg=self.theme["panel_alt"], fg=self.theme["text"])

        self.listen_btn.config(
            bg=self.theme["button_bg"],
            fg=self.theme["button_fg"],
            activebackground=self.theme["accent_alt"],
            activeforeground=self.theme["button_fg"],
        )
        self.settings_btn.config(
            bg=self.theme["secondary_bg"],
            fg=self.theme["secondary_fg"],
            activebackground=self.theme["chip_bg"],
            activeforeground=self.theme["secondary_fg"],
        )

        self._configure_notebook_style()
        self._draw_mic_meter()

    def _configure_notebook_style(self):
        self.ttk_style.configure(
            "Locus.TNotebook",
            background=self.theme["panel"],
            borderwidth=0,
            tabmargins=(0, 0, 0, 0),
        )
        self.ttk_style.configure(
            "Locus.TNotebook.Tab",
            background=self.theme["panel_alt"],
            foreground=self.theme["text"],
            padding=(14, 8),
            borderwidth=0,
        )
        self.ttk_style.map(
            "Locus.TNotebook.Tab",
            background=[("selected", self.theme["chip_bg"])],
            foreground=[("selected", self.theme["chip_fg"])],
        )

    def set_manual_action(self, callback):
        self.manual_action = callback

    def trigger_manual_action(self):
        if self.manual_action:
            self.manual_action()

    def set_status(self, text, tone="idle", detail=None):
        color_key = STATUS_TONES.get(tone, "muted")
        self.status_text.config(text=text, fg=self.theme[color_key])
        if detail is not None:
            self.status_subtext.config(text=detail)

    def set_transcript(self, user_text=None, locus_text=None):
        if user_text is not None:
            self.user_text_label.config(text=user_text)
        if locus_text is not None:
            self.locus_text_label.config(text=locus_text)

    def set_mic_state(self, state, detail=None):
        self.mic_state = state
        labels = {
            "idle": "Idle",
            "listening": "Listening",
            "thinking": "Thinking",
            "error": "Error",
        }
        self.mic_mode_label.config(text=labels.get(state, "Idle"))
        if detail is not None:
            self.status_subtext.config(text=detail)
        if state != "listening":
            self.mic_level = 0.0
        self._draw_mic_meter()

    def update_mic_level(self, level):
        self.mic_level = max(0.0, min(1.0, float(level)))

    def start_visualizer(self, detail="Listening for your voice..."):
        self.set_mic_state("listening", detail)

    def stop_visualizer(self):
        self.mic_level = 0.0
        if self.mic_state == "listening":
            self.set_mic_state("idle", "Ready for the next wake word.")
        else:
            self._draw_mic_meter()

    def _start_bar_loop(self):
        if self.bar_loop_id:
            self.root.after_cancel(self.bar_loop_id)

        speed = ANIMATION_SPEEDS.get(config.ANIMATION_SPEED, ANIMATION_SPEEDS["normal"])
        self.smoothed_level += (self.mic_level - self.smoothed_level) * speed["smoothing"]
        self.bar_tick += 1
        self._draw_mic_meter()
        self.bar_loop_id = self.root.after(speed["delay"], self._start_bar_loop)

    def _draw_mic_meter(self):
        canvas = self.mic_canvas
        canvas.delete("all")

        icon_x = 48
        icon_y = 48
        icon_color = self.theme["danger"] if self.mic_state == "error" else self.theme["accent"]

        canvas.create_oval(icon_x - 12, icon_y - 24, icon_x + 12, icon_y + 4, fill=icon_color, outline="")
        canvas.create_rectangle(icon_x - 12, icon_y - 10, icon_x + 12, icon_y + 4, fill=icon_color, outline="")
        canvas.create_line(icon_x, icon_y + 4, icon_x, icon_y + 24, fill=icon_color, width=4)
        canvas.create_arc(
            icon_x - 20,
            icon_y + 2,
            icon_x + 20,
            icon_y + 32,
            start=200,
            extent=140,
            style="arc",
            outline=icon_color,
            width=4,
        )
        canvas.create_line(icon_x - 14, icon_y + 32, icon_x + 14, icon_y + 32, fill=icon_color, width=4)

        bar_count = 16
        level = self.smoothed_level
        if self.mic_state == "listening":
            active_bars = max(1, int(round(level * bar_count)))
        elif self.mic_state == "thinking":
            active_bars = 2 + (self.bar_tick % 5)
        elif self.mic_state == "error":
            active_bars = 0
        else:
            active_bars = 1

        start_x = 120
        for index in range(bar_count):
            bar_height = 18 + ((index % 4) * 10)
            x1 = start_x + (index * 20)
            y1 = 72 - bar_height
            x2 = x1 + 12
            y2 = 72
            color = self.theme["bar_on"] if index < active_bars else self.theme["bar_off"]
            if self.mic_state == "error":
                color = self.theme["danger"] if index < 4 else self.theme["bar_off"]
            canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="")

        footer = {
            "idle": "Mic level waits here until listening starts.",
            "listening": "These bars use the real microphone level.",
            "thinking": "Processing captured audio.",
            "error": "Microphone is unavailable.",
        }.get(self.mic_state, "Mic level waits here until listening starts.")
        canvas.create_text(120, 14, anchor="w", text=footer, fill=self.theme["muted"], font=("Segoe UI", 9))

    def fade_to_image(self, state):
        if self.animation_id:
            self.root.after_cancel(self.animation_id)
            self.animation_id = None

        path = os.path.join(ASSETS_DIR, f"cat_{state}.jpg")
        if not os.path.exists(path):
            path = os.path.join(ASSETS_DIR, "cat_idle.jpg")

        try:
            next_img = Image.open(path).resize((340, 340), Image.Resampling.LANCZOS).convert("RGBA")
        except Exception as exc:
            print(f"UI ERROR: Could not open image {path}: {exc}")
            return

        if self.current_raw_img is None:
            self.current_raw_img = next_img
            photo = ImageTk.PhotoImage(next_img)
            self.image_label.configure(image=photo)
            self.image_label.image = photo
            return

        steps = 8
        delay_ms = 22
        start_img = self.current_raw_img

        def animate(step):
            blended = Image.blend(start_img, next_img, step / steps)
            photo = ImageTk.PhotoImage(blended)
            self.image_label.configure(image=photo)
            self.image_label.image = photo
            if step < steps:
                self.animation_id = self.root.after(delay_ms, lambda: animate(step + 1))
            else:
                self.current_raw_img = next_img
                self.animation_id = None

        animate(0)

    def open_settings_window(self):
        if self.settings_window and self.settings_window.winfo_exists():
            self.settings_window.focus_force()
            return

        current_settings = load_settings()
        window = tk.Toplevel(self.root)
        self.settings_window = window
        window.title("Settings")
        window.geometry("470x470")
        window.resizable(False, False)
        window.transient(self.root)
        window.grab_set()
        window.config(bg=self.theme["panel"])

        shell = tk.Frame(window, bg=self.theme["panel"])
        shell.pack(fill="both", expand=True, padx=16, pady=16)

        heading = tk.Label(shell, text="Settings", font=("Segoe UI Semibold", 20), bg=self.theme["panel"], fg=self.theme["title"])
        heading.pack(anchor="w")

        subheading = tk.Label(
            shell,
            text="Everything is grouped by topic and saved to data/settings.json.",
            font=("Segoe UI", 9),
            bg=self.theme["panel"],
            fg=self.theme["muted"],
        )
        subheading.pack(anchor="w", pady=(4, 12))

        notebook = ttk.Notebook(shell, style="Locus.TNotebook")
        notebook.pack(fill="both", expand=True)

        general_tab = tk.Frame(notebook, bg=self.theme["panel"])
        voice_tab = tk.Frame(notebook, bg=self.theme["panel"])
        appearance_tab = tk.Frame(notebook, bg=self.theme["panel"])
        notebook.add(general_tab, text="General")
        notebook.add(voice_tab, text="Voice")
        notebook.add(appearance_tab, text="Appearance")

        model_var = tk.StringVar(value=current_settings["gemini_model"])
        language_var = tk.StringVar(value=current_settings["language_code"])
        wake_words_var = tk.StringVar(value=", ".join(current_settings["wake_words"]))
        theme_var = tk.StringVar(value=current_settings["theme"])
        animation_speed_var = tk.StringVar(value=current_settings["animation_speed"])

        self._build_setting_field(general_tab, "Gemini model", model_var, "Example: gemini-flash-latest")
        self._build_setting_field(voice_tab, "Language code", language_var, "Example: en-US")
        self._build_setting_field(voice_tab, "Wake words", wake_words_var, "Comma separated words")
        self._build_theme_selector(appearance_tab, theme_var)
        self._build_speed_selector(appearance_tab, animation_speed_var)

        button_row = tk.Frame(shell, bg=self.theme["panel"])
        button_row.pack(fill="x", pady=(12, 0))

        def close_window():
            self.settings_window = None
            window.destroy()

        def save_and_apply():
            try:
                saved_settings = save_settings(
                    {
                        "gemini_model": model_var.get(),
                        "language_code": language_var.get(),
                        "wake_words": wake_words_var.get(),
                        "theme": theme_var.get(),
                        "animation_speed": animation_speed_var.get(),
                    }
                )
                apply_settings(saved_settings)
                reload_gemini_client()
                self.apply_theme(config.THEME)
                self.hero_caption.config(text="Wake words: " + ", ".join(config.WAKE_WORDS))
                self._start_bar_loop()
                messagebox.showinfo("Settings", "Settings saved.")
                close_window()
            except OSError as exc:
                messagebox.showerror("Settings", f"Could not save settings.\n{exc}")

        cancel_btn = tk.Button(
            button_row,
            text="Cancel",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            bg=self.theme["secondary_bg"],
            fg=self.theme["secondary_fg"],
            command=close_window,
            cursor="hand2",
            padx=16,
            pady=10,
        )
        cancel_btn.pack(side="right", padx=(10, 0))

        save_btn = tk.Button(
            button_row,
            text="Save",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            bg=self.theme["button_bg"],
            fg=self.theme["button_fg"],
            command=save_and_apply,
            cursor="hand2",
            padx=16,
            pady=10,
        )
        save_btn.pack(side="right")

        window.protocol("WM_DELETE_WINDOW", close_window)

    def _build_setting_field(self, parent, label_text, variable, note):
        block = tk.Frame(parent, bg=self.theme["panel_alt"], highlightthickness=1, highlightbackground=self.theme["border"])
        block.pack(fill="x", padx=12, pady=(14, 0))

        label = tk.Label(block, text=label_text, font=("Segoe UI", 10, "bold"), bg=self.theme["panel_alt"], fg=self.theme["title"])
        label.pack(anchor="w", padx=12, pady=(12, 4))

        entry = tk.Entry(
            block,
            textvariable=variable,
            relief="flat",
            font=("Segoe UI", 10),
            bg=self.theme["panel"],
            fg=self.theme["text"],
            insertbackground=self.theme["text"],
        )
        entry.pack(fill="x", padx=12, pady=(0, 6), ipady=8)

        note_label = tk.Label(block, text=note, font=("Segoe UI", 8), bg=self.theme["panel_alt"], fg=self.theme["muted"])
        note_label.pack(anchor="w", padx=12, pady=(0, 12))

    def _build_theme_selector(self, parent, variable):
        block = tk.Frame(parent, bg=self.theme["panel_alt"], highlightthickness=1, highlightbackground=self.theme["border"])
        block.pack(fill="x", padx=12, pady=(14, 0))

        label = tk.Label(block, text="UI style", font=("Segoe UI", 10, "bold"), bg=self.theme["panel_alt"], fg=self.theme["title"])
        label.pack(anchor="w", padx=12, pady=(12, 8))

        for key, (name, description) in THEME_CHOICES.items():
            row = tk.Frame(block, bg=self.theme["panel_alt"])
            row.pack(fill="x", padx=12, pady=(0, 8))

            radio = tk.Radiobutton(
                row,
                text=name,
                value=key,
                variable=variable,
                bg=self.theme["panel_alt"],
                fg=self.theme["text"],
                selectcolor=self.theme["panel"],
                activebackground=self.theme["panel_alt"],
                activeforeground=self.theme["title"],
                font=("Segoe UI", 10, "bold"),
                anchor="w",
            )
            radio.pack(anchor="w")

            desc = tk.Label(row, text=description, font=("Segoe UI", 8), bg=self.theme["panel_alt"], fg=self.theme["muted"])
            desc.pack(anchor="w", padx=(24, 0))

    def _build_speed_selector(self, parent, variable):
        block = tk.Frame(parent, bg=self.theme["panel_alt"], highlightthickness=1, highlightbackground=self.theme["border"])
        block.pack(fill="x", padx=12, pady=(14, 0))

        label = tk.Label(block, text="Animation speed", font=("Segoe UI", 10, "bold"), bg=self.theme["panel_alt"], fg=self.theme["title"])
        label.pack(anchor="w", padx=12, pady=(12, 8))

        options = tk.Frame(block, bg=self.theme["panel_alt"])
        options.pack(fill="x", padx=12, pady=(0, 12))

        for key, text in (("slow", "Slow"), ("normal", "Normal"), ("fast", "Fast")):
            radio = tk.Radiobutton(
                options,
                text=text,
                value=key,
                variable=variable,
                bg=self.theme["panel_alt"],
                fg=self.theme["text"],
                selectcolor=self.theme["panel"],
                activebackground=self.theme["panel_alt"],
                activeforeground=self.theme["title"],
                font=("Segoe UI", 10),
            )
            radio.pack(side="left", padx=(0, 18))
