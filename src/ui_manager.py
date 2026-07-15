import os
import tkinter as tk
from tkinter import messagebox, ttk

from PIL import Image, ImageTk

import src.config as config
from src.actions import reload_gemini_client, validate_gemini_configuration
from src.config import ASSETS_DIR
from src.settings_manager import (
    ANIMATION_SPEED_OPTIONS,
    LANGUAGE_OPTIONS,
    THEME_OPTIONS,
    WAKE_WORD_PRESET_OPTIONS,
    apply_settings,
    get_settings_service,
    load_gemini_api_key,
    load_settings,
    save_gemini_api_key,
    save_settings,
    validate_settings_input,
)


THEMES = {
    "glass_green": {
        "root_bg": "#7E8387",
        "shell": "#152016",
        "shell_border": "#E5ECE6",
        "sidebar": "#102014",
        "panel": "#1B2A1D",
        "panel_alt": "#223525",
        "border": "#36503A",
        "title": "#F2FAF1",
        "text": "#D8F5E5",
        "muted": "#7EA38A",
        "accent": "#00E87A",
        "accent_soft": "#183A24",
        "accent_alt": "#89F59E",
        "accent_dim": "#20492D",
        "success": "#6AFF8B",
        "warning": "#DAF86A",
        "danger": "#FF7B87",
        "button_bg": "#00E87A",
        "button_fg": "#04120A",
        "button_active": "#1DF08C",
        "secondary_bg": "#233127",
        "secondary_fg": "#E3F6E8",
        "secondary_active": "#2A3A2F",
        "chip_bg": "#18281C",
        "chip_fg": "#8FF0AD",
        "status_badge_bg": "#163621",
        "status_badge_fg": "#00E87A",
        "bar_off": "#2E3B31",
        "bar_on": "#00E87A",
        "canvas_bg": "#1B231D",
        "input_bg": "#132117",
        "input_fg": "#E6F7EA",
        "search_bg": "#162619",
        "search_fg": "#D8F5E5",
    },
    "light": {
        "root_bg": "#E4EAEF",
        "shell": "#F3F7F4",
        "shell_border": "#E2E8F0",
        "sidebar": "#FFFFFF",
        "panel": "#FFFFFF",
        "panel_alt": "#F3F7FA",
        "border": "#D7E2E9",
        "title": "#1E293B",
        "text": "#2F3E4F",
        "muted": "#64748B",
        "accent": "#16A34A",
        "accent_soft": "#DCF6E5",
        "accent_alt": "#38BDF8",
        "accent_dim": "#E7F6EC",
        "success": "#16A34A",
        "warning": "#D97706",
        "danger": "#DC2626",
        "button_bg": "#16A34A",
        "button_fg": "#FFFFFF",
        "button_active": "#1DB356",
        "secondary_bg": "#E2E8F0",
        "secondary_fg": "#334155",
        "secondary_active": "#D7E0E9",
        "chip_bg": "#EEF5F0",
        "chip_fg": "#1A7F46",
        "status_badge_bg": "#E8F5EC",
        "status_badge_fg": "#16A34A",
        "bar_off": "#DDE5EE",
        "bar_on": "#16A34A",
        "canvas_bg": "#F7FAFC",
        "input_bg": "#FFFFFF",
        "input_fg": "#1E293B",
        "search_bg": "#F7FAF8",
        "search_fg": "#334155",
    },
    "dark": {
        "root_bg": "#11151C",
        "shell": "#121922",
        "shell_border": "#273240",
        "sidebar": "#0C1017",
        "panel": "#18202A",
        "panel_alt": "#202938",
        "border": "#2E3A49",
        "title": "#F2F6FB",
        "text": "#E3EAF4",
        "muted": "#7C8AA0",
        "accent": "#22C55E",
        "accent_soft": "#173324",
        "accent_alt": "#38BDF8",
        "accent_dim": "#1B2F24",
        "success": "#4ADE80",
        "warning": "#F59E0B",
        "danger": "#F87171",
        "button_bg": "#22C55E",
        "button_fg": "#08120B",
        "button_active": "#2ED56A",
        "secondary_bg": "#243140",
        "secondary_fg": "#E2E8F0",
        "secondary_active": "#2D3B4D",
        "chip_bg": "#14202D",
        "chip_fg": "#93C5FD",
        "status_badge_bg": "#183223",
        "status_badge_fg": "#22C55E",
        "bar_off": "#304154",
        "bar_on": "#22C55E",
        "canvas_bg": "#101822",
        "input_bg": "#0F172A",
        "input_fg": "#E2E8F0",
        "search_bg": "#101722",
        "search_fg": "#D8E2EE",
    },
    "colorful": {
        "root_bg": "#DDD8F4",
        "shell": "#1A1029",
        "shell_border": "#F5D0FE",
        "sidebar": "#12091F",
        "panel": "#241736",
        "panel_alt": "#312047",
        "border": "#5A3E73",
        "title": "#FFF7ED",
        "text": "#F3E8FF",
        "muted": "#B695D2",
        "accent": "#F97316",
        "accent_soft": "#472514",
        "accent_alt": "#F472B6",
        "accent_dim": "#4A2B1E",
        "success": "#4ADE80",
        "warning": "#FACC15",
        "danger": "#FB7185",
        "button_bg": "#F97316",
        "button_fg": "#FFF7ED",
        "button_active": "#FF8B37",
        "secondary_bg": "#3B2854",
        "secondary_fg": "#F8E9FF",
        "secondary_active": "#493564",
        "chip_bg": "#3B2B52",
        "chip_fg": "#F9A8D4",
        "status_badge_bg": "#4A2A16",
        "status_badge_fg": "#F97316",
        "bar_off": "#4C3D61",
        "bar_on": "#F97316",
        "canvas_bg": "#23192F",
        "input_bg": "#241735",
        "input_fg": "#F6EDFF",
        "search_bg": "#2A1B3D",
        "search_fg": "#F3E8FF",
    },
}

ANIMATION_SPEEDS = {
    "slow": {"delay": 80, "smoothing": 0.15},
    "normal": {"delay": 55, "smoothing": 0.22},
    "fast": {"delay": 35, "smoothing": 0.30},
}

STATUS_TONES = {
    "idle": "muted",
    "listening": "accent",
    "thinking": "accent_alt",
    "prompt": "warning",
    "success": "success",
    "error": "danger",
}

THEME_SWITCH_ORDER = ("glass_green", "dark", "light", "colorful")
THEME_SHORT_LABELS = {
    "glass_green": "Glass",
    "dark": "Dark",
    "light": "Light",
    "colorful": "Color",
}


class LocusUI:
    def __init__(self, root):
        self.root = root
        self.current_raw_img = None
        self.animation_id = None
        self.manual_action = None
        self.settings_window = None
        self.current_theme_name = config.THEME
        self.theme = THEMES.get(self.current_theme_name, THEMES["glass_green"])

        self.mic_state = "idle"
        self.mic_level = 0.0
        self.smoothed_level = 0.0
        self.bar_loop_id = None
        self.bar_tick = 0
        self.conversation_messages = []

        self.root.title("Locus AI")
        self.root.geometry("1320x820")
        self.root.minsize(1180, 760)

        self._configure_styles()
        self._build_layout()
        self.apply_theme()
        self.fade_to_image("idle")
        self.set_status("Say 'Locus'", "idle", "Left-click the cat or wait for the wake word.")
        self.set_transcript(
            user_text="Waiting for your command.",
            locus_text="I am ready. Say the wake word or start listening manually.",
        )
        self._start_bar_loop()
        self.root.bind("<Configure>", self._handle_resize)

    def _configure_styles(self):
        self.ttk_style = ttk.Style()
        try:
            self.ttk_style.theme_use("clam")
        except tk.TclError:
            pass

    def _build_layout(self):
        self._build_shell()
        self._build_top_bar()
        self._build_content_area()
        self._build_sidebar()
        self._build_dashboard()
        self._build_assistant_panel()
        self._build_voice_panel()
        self._build_conversation_panel()
        self._build_session_panel()

    def _build_shell(self):
        self.main_frame = tk.Frame(self.root, bd=0, highlightthickness=0)
        self.main_frame.pack(fill="both", expand=True, padx=22, pady=22)

        self.shell_frame = tk.Frame(self.main_frame, bd=0, highlightthickness=1)
        self.shell_frame.pack(fill="both", expand=True)

        self.body_frame = tk.Frame(self.shell_frame, bd=0, highlightthickness=0)
        self.body_frame.pack(fill="both", expand=True)

        self.main_column = tk.Frame(self.body_frame, bd=0, highlightthickness=0)
        self.main_column.pack(side="left", fill="both", expand=True)

    def _build_top_bar(self):
        self.top_bar = tk.Frame(self.main_column, bd=0, highlightthickness=0)
        self.top_bar.pack(fill="x", padx=28, pady=(24, 18))

        self.brand_block = tk.Frame(self.top_bar, bd=0, highlightthickness=0)
        self.brand_block.pack(side="left", fill="x", expand=True)

        self.title_label = tk.Label(
            self.brand_block,
            text="Locus AI",
            font=("Segoe UI Semibold", 30),
            anchor="w",
        )
        self.title_label.pack(anchor="w")

        self.subtitle_label = tk.Label(
            self.brand_block,
            text="Voice assistant with local intents, Gemini fallback, and reactive cat states.",
            font=("Segoe UI", 11),
            anchor="w",
        )
        self.subtitle_label.pack(anchor="w", pady=(4, 0))

        self.utility_block = tk.Frame(self.top_bar, bd=0, highlightthickness=0)
        self.utility_block.pack(side="right", anchor="n")

        self.search_shell = tk.Frame(self.utility_block, bd=0, highlightthickness=0)
        self.search_shell.pack(side="left", padx=(0, 16))

        self.search_icon = tk.Label(
            self.search_shell,
            text="⌕  Search",
            font=("Segoe UI", 10),
            padx=14,
            pady=9,
            anchor="w",
            width=18,
        )
        self.search_icon.pack(fill="x")

        self.theme_badge = tk.Label(
            self.utility_block,
            text="Glass Green",
            font=("Segoe UI", 9, "bold"),
            padx=12,
            pady=9,
        )
        self.theme_badge.pack(side="left", padx=(0, 10))

        self.theme_switcher = tk.Frame(self.utility_block, bd=0, highlightthickness=0)
        self.theme_switcher.pack(side="left", padx=(0, 10))

        self.theme_buttons = {}
        for theme_name in THEME_SWITCH_ORDER:
            button = tk.Button(
                self.theme_switcher,
                text=THEME_SHORT_LABELS[theme_name],
                font=("Segoe UI", 8, "bold"),
                relief="flat",
                cursor="hand2",
                command=lambda selected=theme_name: self.apply_theme(selected),
                padx=10,
                pady=6,
            )
            button.pack(side="left", padx=(0, 4))
            self.theme_buttons[theme_name] = button

        self.top_status_chip = tk.Label(
            self.utility_block,
            text="Idle",
            font=("Segoe UI", 9, "bold"),
            padx=12,
            pady=9,
        )
        self.top_status_chip.pack(side="left")

    def _build_content_area(self):
        self.content_frame = tk.Frame(self.main_column, bd=0, highlightthickness=0)
        self.content_frame.pack(fill="both", expand=True, padx=28, pady=(0, 28))

    def _build_sidebar(self):
        self.rail_card = self._create_card(self.body_frame)
        self.rail_card.pack(side="left", fill="y", padx=(24, 18), pady=24)

        self.rail_inner = tk.Frame(self.rail_card, bd=0, highlightthickness=0)
        self.rail_inner.pack(fill="y", expand=True, padx=12, pady=14)

        self.rail_brand = tk.Frame(self.rail_inner, width=52, height=128, bd=0, highlightthickness=0)
        self.rail_brand.pack(fill="x", pady=(0, 18))
        self.rail_brand.pack_propagate(False)

        self.rail_brand_fill = tk.Frame(self.rail_brand, bd=0, highlightthickness=0)
        self.rail_brand_fill.pack(fill="both", expand=True)

        self.rail_nav = tk.Frame(self.rail_inner, bd=0, highlightthickness=0)
        self.rail_nav.pack(fill="x")

        self.rail_items = []
        for icon_text, label_text, is_active in (
            ("⌂", "HOME", True),
            ("◉", "MIC", False),
            ("✦", "CHAT", False),
            ("⚙", "SET", False),
        ):
            item_frame = tk.Frame(self.rail_nav, bd=0, highlightthickness=0, cursor="hand2")
            item_frame.pack(fill="x", pady=6)

            icon = tk.Label(
                item_frame,
                text=icon_text,
                font=("Segoe UI Symbol", 14),
                anchor="center",
                cursor="hand2",
            )
            icon.pack(anchor="center", pady=(8, 2))

            label = tk.Label(
                item_frame,
                text=label_text,
                font=("Segoe UI", 8, "bold"),
                width=6,
                anchor="center",
                cursor="hand2",
            )
            label.pack(fill="x", pady=(0, 8))

            self.rail_items.append(
                {
                    "frame": item_frame,
                    "icon": icon,
                    "label": label,
                    "active": is_active,
                }
            )

        self.rail_footer_frame = tk.Frame(self.rail_inner, bd=0, highlightthickness=0)
        self.rail_footer_frame.pack(side="bottom", fill="x")

        self.rail_footer_icon = tk.Label(
            self.rail_footer_frame,
            text="◌",
            font=("Segoe UI Symbol", 14),
            anchor="center",
        )
        self.rail_footer_icon.pack(anchor="center", pady=(8, 2))

        self.rail_footer = tk.Label(
            self.rail_footer_frame,
            text="VOICE",
            font=("Segoe UI", 8, "bold"),
        )
        self.rail_footer.pack(side="bottom", fill="x", pady=(0, 8))

    def _build_dashboard(self):
        self.dashboard_frame = tk.Frame(self.content_frame, bd=0, highlightthickness=0)
        self.dashboard_frame.pack(fill="both", expand=True)
        self.dashboard_frame.grid_columnconfigure(0, weight=3)
        self.dashboard_frame.grid_columnconfigure(1, weight=2)
        self.dashboard_frame.grid_rowconfigure(0, weight=2)
        self.dashboard_frame.grid_rowconfigure(1, weight=2)

    def _build_assistant_panel(self):
        self.hero_card = self._create_card(self.dashboard_frame)
        self.hero_card.grid(row=0, column=0, sticky="nsew", padx=(0, 16), pady=(0, 16))

        self.hero_header = tk.Frame(self.hero_card, bd=0, highlightthickness=0)
        self.hero_header.pack(fill="x", padx=22, pady=(20, 12))

        self.hero_title = tk.Label(
            self.hero_header,
            text="Assistant",
            font=("Segoe UI Semibold", 17),
            anchor="w",
        )
        self.hero_title.pack(side="left")

        self.hero_hint = tk.Label(
            self.hero_header,
            text="Click the cat to wake it",
            font=("Segoe UI", 9, "bold"),
            padx=12,
            pady=6,
        )
        self.hero_hint.pack(side="right")

        self.hero_body = tk.Frame(self.hero_card, bd=0, highlightthickness=0)
        self.hero_body.pack(fill="both", expand=True, padx=22, pady=(0, 18))
        self.hero_body.grid_columnconfigure(0, weight=0)
        self.hero_body.grid_columnconfigure(1, weight=1)

        self.image_frame = tk.Frame(self.hero_body, bd=0, highlightthickness=0, width=142)
        self.image_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 16))
        self.image_frame.grid_propagate(False)

        self.image_label = tk.Label(self.image_frame, cursor="hand2", bd=0, highlightthickness=0)
        self.image_label.pack(fill="both", expand=True)

        self.hero_overlay = tk.Frame(self.image_frame, bd=0, highlightthickness=0)
        self.hero_overlay.place(relx=0, rely=1, relwidth=1, anchor="sw")

        self.hero_overlay_title = tk.Label(
            self.hero_overlay,
            text="Go ahead",
            font=("Segoe UI Semibold", 13),
            anchor="w",
            padx=12,
            pady=6,
        )
        self.hero_overlay_title.pack(fill="x")

        self.hero_caption = tk.Label(
            self.hero_overlay,
            text="Wake words: " + ", ".join(config.WAKE_WORDS),
            font=("Segoe UI", 9),
            anchor="w",
            justify="left",
            padx=12,
            pady=0,
        )
        self.hero_caption.pack(fill="x", pady=(0, 10))

        self.hero_side = tk.Frame(self.hero_body, bd=0, highlightthickness=0)
        self.hero_side.grid(row=0, column=1, sticky="nsew")
        self.hero_side.grid_rowconfigure(4, weight=1)

        self.hero_side_title = tk.Label(
            self.hero_side,
            text="Control Deck",
            font=("Segoe UI Semibold", 15),
            anchor="w",
        )
        self.hero_side_title.pack(fill="x")

        self.hero_side_copy = tk.Label(
            self.hero_side,
            text="Manual wake, visual status, and wake-word cues live here.",
            font=("Segoe UI", 9),
            justify="left",
            anchor="w",
            wraplength=280,
        )
        self.hero_side_copy.pack(fill="x", pady=(6, 12))

        self.listen_btn = tk.Button(
            self.hero_side,
            text="Listen",
            font=("Segoe UI", 11, "bold"),
            relief="flat",
            command=self.trigger_manual_action,
            cursor="hand2",
            padx=18,
            pady=14,
        )
        self.listen_btn.pack(fill="x", pady=(0, 10))

        self.settings_btn = tk.Button(
            self.hero_side,
            text="Settings",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            command=self.open_settings_window,
            cursor="hand2",
            padx=18,
            pady=12,
        )
        self.settings_btn.pack(fill="x", pady=(0, 14))

        self.quick_stats = []
        for label_text in ("Wake Word Ready", "Manual Trigger Enabled", "Gemini Standby"):
            chip = tk.Label(
                self.hero_side,
                text=label_text,
                font=("Segoe UI", 9, "bold"),
                anchor="w",
                padx=12,
                pady=8,
            )
            chip.pack(fill="x", pady=(0, 6))
            self.quick_stats.append(chip)

    def _build_voice_panel(self):
        self.mic_card = self._create_card(self.dashboard_frame)
        self.mic_card.grid(row=0, column=1, sticky="nsew", pady=(0, 16))

        self.mic_header = tk.Frame(self.mic_card, bd=0, highlightthickness=0)
        self.mic_header.pack(fill="x", padx=22, pady=(20, 10))

        self.status_text = tk.Label(
            self.mic_header,
            text="Say 'Locus'",
            font=("Segoe UI Semibold", 17),
            anchor="w",
        )
        self.status_text.pack(side="left")

        self.mic_mode_label = tk.Label(
            self.mic_header,
            text="Idle",
            font=("Segoe UI", 9, "bold"),
            padx=12,
            pady=6,
        )
        self.mic_mode_label.pack(side="right")

        self.voice_intro = tk.Label(
            self.mic_card,
            text="Left-click the cat or wait for the wake word.",
            font=("Segoe UI", 10),
            anchor="w",
            justify="left",
        )
        self.voice_intro.pack(fill="x", padx=22, pady=(0, 10))

        self.voice_meta = tk.Frame(self.mic_card, bd=0, highlightthickness=0)
        self.voice_meta.pack(fill="x", padx=22, pady=(0, 10))

        self.voice_meta_label = tk.Label(
            self.voice_meta,
            text="Voice Activity",
            font=("Segoe UI", 10, "bold"),
            anchor="w",
        )
        self.voice_meta_label.pack(side="left")

        self.voice_meta_state = tk.Label(
            self.voice_meta,
            text="Passive",
            font=("Segoe UI", 9, "bold"),
            padx=10,
            pady=4,
        )
        self.voice_meta_state.pack(side="right")

        self.status_subtext = tk.Label(
            self.mic_card,
            text="Waiting for activation",
            font=("Segoe UI", 9),
            anchor="w",
            justify="left",
        )
        self.status_subtext.pack(fill="x", padx=22, pady=(0, 12))

        self.mic_canvas = tk.Canvas(self.mic_card, height=182, bd=0, highlightthickness=0)
        self.mic_canvas.pack(fill="both", expand=True, padx=20, pady=(0, 10))

        self.history_canvas = tk.Canvas(self.mic_card, height=42, bd=0, highlightthickness=0)
        self.history_canvas.pack(fill="x", padx=20, pady=(0, 20))

    def _build_conversation_panel(self):
        self.transcript_card = self._create_card(self.dashboard_frame)
        self.transcript_card.grid(row=1, column=0, sticky="nsew", padx=(0, 16))

        self.transcript_header = tk.Frame(self.transcript_card, bd=0, highlightthickness=0)
        self.transcript_header.pack(fill="x", padx=22, pady=(20, 12))

        self.transcript_title = tk.Label(
            self.transcript_header,
            text="Conversation",
            font=("Segoe UI Semibold", 17),
            anchor="w",
        )
        self.transcript_title.pack(side="left")

        self.transcript_chip = tk.Label(
            self.transcript_header,
            text="Live Preview",
            font=("Segoe UI", 9, "bold"),
            padx=12,
            pady=6,
        )
        self.transcript_chip.pack(side="right")

        self.transcript_canvas = tk.Canvas(self.transcript_card, bd=0, highlightthickness=0)
        self.transcript_canvas.pack(fill="both", expand=True, padx=(20, 8), pady=(0, 20), side="left")

        self.transcript_scrollbar = ttk.Scrollbar(
            self.transcript_card,
            orient="vertical",
            command=self.transcript_canvas.yview,
        )
        self.transcript_scrollbar.pack(fill="y", side="right", padx=(0, 14), pady=(0, 20))
        self.transcript_canvas.configure(yscrollcommand=self.transcript_scrollbar.set)

        self.transcript_content = tk.Frame(self.transcript_canvas, bd=0, highlightthickness=0)
        self.transcript_window = self.transcript_canvas.create_window((0, 0), window=self.transcript_content, anchor="nw")
        self.transcript_content.bind("<Configure>", self._sync_transcript_scrollregion)
        self.transcript_canvas.bind("<Configure>", self._resize_transcript_content)

        self.message_widgets = []
        self.user_text_label = None
        self.locus_text_label = None

    def _build_session_panel(self):
        self.control_card = self._create_card(self.dashboard_frame)
        self.control_card.grid(row=1, column=1, sticky="nsew")

        self.control_header = tk.Frame(self.control_card, bd=0, highlightthickness=0)
        self.control_header.pack(fill="x", padx=22, pady=(20, 12))

        self.control_title = tk.Label(
            self.control_header,
            text="Session Summary",
            font=("Segoe UI Semibold", 17),
            anchor="w",
        )
        self.control_title.pack(side="left")

        self.control_chip = tk.Label(
            self.control_header,
            text="Dashboard",
            font=("Segoe UI", 9, "bold"),
            padx=12,
            pady=6,
        )
        self.control_chip.pack(side="right")

        self.summary_rows = []
        for heading, detail in (
            ("Model", config.MODEL_NAME),
            ("Wake Words", ", ".join(config.WAKE_WORDS)),
            ("Interaction", "Waiting for the next command."),
            ("Audio", "Input: system default"),
        ):
            row = tk.Frame(self.control_card, bd=0, highlightthickness=1)
            row.pack(fill="x", padx=20, pady=(0, 8))

            title = tk.Label(row, text=heading, font=("Segoe UI", 9, "bold"), anchor="w")
            title.pack(fill="x", padx=14, pady=(10, 2))

            copy = tk.Label(
                row,
                text=detail,
                font=("Segoe UI", 9),
                justify="left",
                anchor="w",
                wraplength=300,
            )
            copy.pack(fill="x", padx=14, pady=(0, 10))
            self.summary_rows.append((row, title, copy))
        self.footer_note = None

    def _create_card(self, parent):
        return tk.Frame(parent, bd=0, highlightthickness=1)

    def _set_button_colors(self, button, bg, fg, active_bg):
        button.config(
            bg=bg,
            fg=fg,
            activebackground=active_bg,
            activeforeground=fg,
            highlightthickness=0,
            bd=0,
        )

    def _set_theme_switch_button_colors(self):
        for theme_name, button in self.theme_buttons.items():
            is_selected = theme_name == self.current_theme_name
            bg = self.theme["button_bg"] if is_selected else self.theme["search_bg"]
            fg = self.theme["button_fg"] if is_selected else self.theme["muted"]
            active_bg = self.theme["button_active"] if is_selected else self.theme["secondary_active"]
            self._set_button_colors(button, bg, fg, active_bg)

    def _apply_sidebar_item_styles(self):
        for item in self.rail_items:
            is_active = item["active"]
            frame_bg = self.theme["accent_dim"] if is_active else self.theme["sidebar"]
            text_fg = self.theme["accent"] if is_active else self.theme["muted"]

            item["frame"].config(bg=frame_bg, highlightbackground=frame_bg)
            item["icon"].config(bg=frame_bg, fg=text_fg)
            item["label"].config(
                bg=frame_bg,
                fg=text_fg,
                highlightbackground=frame_bg,
                activebackground=frame_bg,
                activeforeground=text_fg,
            )

        self.rail_footer_frame.config(bg=self.theme["sidebar"])
        self.rail_footer_icon.config(bg=self.theme["sidebar"], fg=self.theme["muted"])
        self.rail_footer.config(bg=self.theme["sidebar"], fg=self.theme["muted"])

    def apply_theme(self, theme_name=None):
        if theme_name:
            self.current_theme_name = theme_name
        self.theme = THEMES.get(self.current_theme_name, THEMES["glass_green"])

        self.root.config(bg=self.theme["root_bg"])
        self.main_frame.config(bg=self.theme["root_bg"])
        self.shell_frame.config(bg=self.theme["shell"], highlightbackground=self.theme["shell_border"])
        self.body_frame.config(bg=self.theme["shell"])
        self.main_column.config(bg=self.theme["shell"])

        for widget in (
            self.top_bar,
            self.brand_block,
            self.utility_block,
            self.search_shell,
            self.theme_switcher,
            self.content_frame,
            self.dashboard_frame,
            self.hero_body,
            self.rail_nav,
        ):
            widget.config(bg=self.theme["shell"])

        for widget in (
            self.hero_header,
            self.hero_side,
            self.mic_header,
            self.voice_meta,
            self.transcript_header,
            self.control_header,
        ):
            widget.config(bg=self.theme["panel"])

        self.title_label.config(bg=self.theme["shell"], fg=self.theme["title"])
        self.subtitle_label.config(bg=self.theme["shell"], fg=self.theme["muted"])
        self.search_icon.config(bg=self.theme["search_bg"], fg=self.theme["search_fg"])

        theme_title = THEME_OPTIONS.get(self.current_theme_name, THEME_OPTIONS["glass_green"])["label"]
        self.theme_badge.config(bg=self.theme["chip_bg"], fg=self.theme["chip_fg"], text=theme_title)
        self._set_theme_switch_button_colors()
        self.top_status_chip.config(
            bg=self.theme["status_badge_bg"],
            fg=self.theme["status_badge_fg"],
            text=f"● {self.mic_mode_label.cget('text')}",
        )

        for widget in (self.rail_card, self.hero_card, self.mic_card, self.transcript_card, self.control_card):
            widget.config(bg=self.theme["panel"], highlightbackground=self.theme["border"])

        self.rail_inner.config(bg=self.theme["sidebar"])
        self.rail_card.config(bg=self.theme["sidebar"], highlightbackground=self.theme["border"])
        self.rail_brand.config(bg=self.theme["sidebar"])
        self.rail_brand_fill.config(bg=self.theme["accent"])
        self._apply_sidebar_item_styles()

        self.hero_title.config(bg=self.theme["panel"], fg=self.theme["title"])
        self.hero_hint.config(bg=self.theme["chip_bg"], fg=self.theme["chip_fg"])
        self.image_frame.config(bg=self.theme["panel"])
        self.image_label.config(bg=self.theme["panel"])
        self.hero_overlay.config(bg=self.theme["accent_dim"])
        self.hero_overlay_title.config(bg=self.theme["accent_dim"], fg=self.theme["title"])
        self.hero_caption.config(bg=self.theme["accent_dim"], fg=self.theme["text"])
        self.hero_side_title.config(bg=self.theme["panel"], fg=self.theme["title"])
        self.hero_side_copy.config(bg=self.theme["panel"], fg=self.theme["muted"])

        for chip in self.quick_stats:
            chip.config(bg=self.theme["accent_dim"], fg=self.theme["accent"])

        status_color = self.theme[STATUS_TONES.get(self.mic_state, "muted")]
        self.status_text.config(bg=self.theme["panel"], fg=status_color)
        self.mic_mode_label.config(bg=self.theme["chip_bg"], fg=self.theme["chip_fg"])
        self.voice_intro.config(bg=self.theme["panel"], fg=self.theme["muted"])
        self.voice_meta_label.config(bg=self.theme["panel"], fg=self.theme["title"])
        self.voice_meta_state.config(bg=self.theme["chip_bg"], fg=self.theme["chip_fg"])
        self.status_subtext.config(bg=self.theme["panel"], fg=self.theme["muted"])
        self.mic_canvas.config(bg=self.theme["canvas_bg"])
        self.history_canvas.config(bg=self.theme["panel"])

        self.transcript_title.config(bg=self.theme["panel"], fg=self.theme["title"])
        self.transcript_chip.config(bg=self.theme["chip_bg"], fg=self.theme["chip_fg"])
        self.transcript_canvas.config(bg=self.theme["panel"])
        self.transcript_content.config(bg=self.theme["panel"])
        self._apply_conversation_theme()

        self.control_title.config(bg=self.theme["panel"], fg=self.theme["title"])
        self.control_chip.config(bg=self.theme["chip_bg"], fg=self.theme["chip_fg"])
        for row, title, copy in self.summary_rows:
            row.config(bg=self.theme["panel_alt"], highlightbackground=self.theme["border"])
            title.config(bg=self.theme["panel_alt"], fg=self.theme["muted"])
            copy.config(bg=self.theme["panel_alt"], fg=self.theme["text"])
        if self.footer_note:
            self.footer_note.config(bg=self.theme["panel"], fg=self.theme["muted"])

        self._set_button_colors(self.listen_btn, self.theme["button_bg"], self.theme["button_fg"], self.theme["button_active"])
        self._set_button_colors(self.settings_btn, self.theme["secondary_bg"], self.theme["secondary_fg"], self.theme["secondary_active"])

        self._configure_notebook_style()
        self._draw_mic_meter()
        self._refresh_dynamic_copy()

    def _configure_notebook_style(self):
        self.ttk_style.configure(
            "Locus.TNotebook",
            background=self.theme["panel"],
            borderwidth=0,
            tabmargins=(0, 0, 0, 0),
        )
        self.ttk_style.configure(
            "Locus.TNotebook.Tab",
            background=self.theme["shell"],
            foreground=self.theme["muted"],
            padding=(18, 12),
            borderwidth=0,
            font=("Segoe UI", 9, "bold"),
        )
        self.ttk_style.map(
            "Locus.TNotebook.Tab",
            background=[("selected", self.theme["chip_bg"]), ("active", self.theme["panel_alt"])],
            foreground=[("selected", self.theme["chip_fg"]), ("active", self.theme["text"])],
        )

    def _refresh_dynamic_copy(self):
        if self.summary_rows:
            self.summary_rows[0][2].config(text=config.MODEL_NAME)
            self.summary_rows[1][2].config(text=", ".join(config.WAKE_WORDS))
            self.summary_rows[3][2].config(text=self._build_audio_summary())
        self.hero_caption.config(text="Wake words: " + ", ".join(config.WAKE_WORDS))
        self._update_quick_stats()

    def _build_audio_summary(self):
        input_label = config.MICROPHONE_DEVICE_ID or "system default"
        output_label = getattr(config, "OUTPUT_AUDIO_DEVICE_ID", "") or "system default"
        return f"Input: {input_label}\nOutput: {output_label}"

    def _update_quick_stats(self):
        gemini_ready = "Gemini Ready" if str(config.GOOGLE_API_KEY or "").strip() else "Gemini Disabled"
        labels = [
            "Wake Word Ready",
            "Manual Trigger Enabled",
            gemini_ready,
        ]
        for chip, label_text in zip(self.quick_stats, labels):
            chip.config(text=label_text)

    def _conversation_role_colors(self, role):
        if role == "user":
            return self.theme["panel_alt"], self.theme["muted"]
        return self.theme["accent_dim"], self.theme["accent"]

    def _apply_conversation_theme(self):
        for message in self.message_widgets:
            bubble_bg, role_fg = self._conversation_role_colors(message["role"])
            message["frame"].config(bg=bubble_bg, highlightbackground=self.theme["border"])
            message["role_label"].config(bg=bubble_bg, fg=role_fg)
            message["text_label"].config(bg=bubble_bg, fg=self.theme["text"])

    def _sync_transcript_scrollregion(self, _event=None):
        self.transcript_canvas.configure(scrollregion=self.transcript_canvas.bbox("all"))

    def _resize_transcript_content(self, event):
        self.transcript_canvas.itemconfigure(self.transcript_window, width=event.width)

    def _scroll_conversation_to_bottom(self):
        self.root.after(10, lambda: self.transcript_canvas.yview_moveto(1.0))

    def _append_conversation_message(self, role, text):
        normalized = " ".join(str(text).split())
        if not normalized:
            return None

        bubble_bg, role_fg = self._conversation_role_colors(role)
        card = tk.Frame(self.transcript_content, bd=0, highlightthickness=1)
        card.pack(fill="x", pady=(0, 10))

        role_text = "You" if role == "user" else "Locus"
        role_label = tk.Label(card, text=role_text, font=("Segoe UI", 9, "bold"), anchor="w")
        role_label.pack(fill="x", padx=14, pady=(12, 4))

        text_label = tk.Label(
            card,
            text=normalized,
            font=("Segoe UI", 11),
            justify="left",
            anchor="w",
            wraplength=520,
        )
        text_label.pack(fill="x", padx=14, pady=(0, 12))

        message = {
            "role": role,
            "frame": card,
            "role_label": role_label,
            "text_label": text_label,
        }
        self.message_widgets.append(message)
        self.conversation_messages.append({"role": role, "text": normalized})
        self._apply_conversation_theme()
        self._scroll_conversation_to_bottom()
        return text_label

    def set_manual_action(self, callback):
        self.manual_action = callback

    def trigger_manual_action(self):
        if self.manual_action:
            self.manual_action()

    def set_status(self, text, tone="idle", detail=None):
        color_key = STATUS_TONES.get(tone, "muted")
        self.status_text.config(text=text, fg=self.theme[color_key])
        self.hero_overlay_title.config(text=text)
        if self.summary_rows:
            self.summary_rows[2][2].config(text=detail or text)
        self.voice_intro.config(text=detail or text)
        if detail is not None:
            self.status_subtext.config(text=detail)

    def set_transcript(self, user_text=None, locus_text=None):
        if user_text is not None:
            self.user_text_label = self._append_conversation_message("user", user_text)
        if locus_text is not None:
            self.locus_text_label = self._append_conversation_message("locus", locus_text)

    def set_mic_state(self, state, detail=None):
        self.mic_state = state
        labels = {
            "idle": "Idle",
            "listening": "Listening",
            "thinking": "Thinking",
            "error": "Error",
        }
        label = labels.get(state, "Idle")
        color_key = STATUS_TONES.get(state, "muted")
        self.mic_mode_label.config(text=label, fg=self.theme["chip_fg"])
        self.top_status_chip.config(text=f"* {label}", fg=self.theme[color_key])
        self.voice_meta_state.config(
            text="Live" if state == "listening" else "Processing" if state == "thinking" else "Passive" if state == "idle" else "Error",
            fg=self.theme["chip_fg"],
        )
        self.status_text.config(fg=self.theme[color_key])
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

        width = max(canvas.winfo_width(), 280)
        height = max(canvas.winfo_height(), 120)
        count = 24
        gap = 5
        start_x = 14
        usable_width = width - (start_x * 2)
        bar_width = max(6, int((usable_width - (gap * (count - 1))) / count))
        baseline = height - 18

        for index in range(count):
            x1 = start_x + index * (bar_width + gap)
            x2 = x1 + bar_width

            if self.mic_state == "listening":
                raw = 10 + int((self.smoothed_level * 55)) + abs(((self.bar_tick + index) % 8) - 4) * 3
                fill = self.theme["bar_on"] if index % 3 != 0 else self.theme["accent"]
            elif self.mic_state == "thinking":
                raw = 8 + abs(((self.bar_tick + index) % 10) - 5) * 4
                fill = self.theme["accent_alt"] if index % 4 == 0 else self.theme["bar_off"]
            elif self.mic_state == "error":
                raw = 6 + (2 if index < 4 else 0)
                fill = self.theme["danger"] if index < 5 else self.theme["bar_off"]
            else:
                raw = 4 + (index % 5)
                fill = self.theme["bar_off"]

            bar_height = min(46, raw)
            y1 = baseline - bar_height
            y2 = baseline
            canvas.create_rectangle(x1, y1, x2, y2, fill=fill, outline="")

        self._draw_voice_history_strip()

    def _draw_voice_history_strip(self):
        canvas = self.history_canvas
        canvas.delete("all")

        width = max(canvas.winfo_width(), 220)
        height = max(canvas.winfo_height(), 36)
        count = 20
        gap = 4
        start_x = 10
        usable_width = width - (start_x * 2)
        bar_width = max(4, int((usable_width - (gap * (count - 1))) / count))

        for index in range(count):
            x1 = start_x + index * (bar_width + gap)
            x2 = x1 + bar_width
            static_height = 6 + abs((index % 7) - 3) * 3

            if self.mic_state == "listening":
                dynamic_height = 8 + abs(((self.bar_tick + index) % 9) - 4) * 3
                fill = self.theme["accent"] if index % 3 == 0 else self.theme["accent_dim"]
            elif self.mic_state == "thinking":
                dynamic_height = 10 + abs(((self.bar_tick + index) % 6) - 3) * 3
                fill = self.theme["accent_alt"] if index % 4 == 0 else self.theme["accent_dim"]
            elif self.mic_state == "error":
                dynamic_height = static_height
                fill = self.theme["danger"] if index < 5 else self.theme["bar_off"]
            else:
                dynamic_height = static_height
                fill = self.theme["bar_off"]

            y1 = height - dynamic_height - 4
            y2 = height - 4
            canvas.create_rectangle(x1, y1, x2, y2, fill=fill, outline="")

    def fade_to_image(self, state):
        if self.animation_id:
            self.root.after_cancel(self.animation_id)
            self.animation_id = None

        path = os.path.join(ASSETS_DIR, f"cat_{state}.jpg")
        if not os.path.exists(path):
            path = os.path.join(ASSETS_DIR, "cat_idle.jpg")

        try:
            next_img = Image.open(path).resize((345, 250), Image.Resampling.LANCZOS).convert("RGBA")
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

    def _handle_resize(self, event):
        if event.widget is not self.root:
            return

        transcript_width = max(260, self.transcript_card.winfo_width() - 80)
        control_width = max(220, self.control_card.winfo_width() - 80)
        for message in self.message_widgets:
            message["text_label"].config(wraplength=transcript_width)
        for _, _, copy in self.summary_rows:
            copy.config(wraplength=control_width)
        self._draw_mic_meter()

    def open_settings_window(self):
        if self.settings_window and self.settings_window.winfo_exists():
            self.settings_window.focus_force()
            return

        settings_service = get_settings_service()
        current_settings = load_settings()
        input_devices = [{"id": "", "label": "System default input"}] + settings_service.list_input_audio_devices()
        output_devices = [{"id": "", "label": "System default output"}] + settings_service.list_output_audio_devices()
        self._append_stale_device(input_devices, current_settings["microphone_device_id"], "Unavailable saved input")
        self._append_stale_device(output_devices, current_settings["output_audio_device_id"], "Unavailable saved output")

        error_labels = {}
        window = tk.Toplevel(self.root)
        self.settings_window = window
        window.title("Settings")
        window.geometry("760x860")
        window.minsize(760, 860)
        window.transient(self.root)
        window.grab_set()
        window.config(bg=self.theme["root_bg"])

        shell = tk.Frame(window, bg=self.theme["shell"], highlightthickness=1, highlightbackground=self.theme["shell_border"])
        shell.pack(fill="both", expand=True, padx=20, pady=20)

        settings_sidebar = tk.Frame(shell, bg=self.theme["sidebar"], width=96, highlightthickness=0)
        settings_sidebar.pack(side="left", fill="y")
        settings_sidebar.pack_propagate(False)

        settings_sidebar_inner = tk.Frame(settings_sidebar, bg=self.theme["sidebar"])
        settings_sidebar_inner.pack(fill="both", expand=True, padx=14, pady=18)

        settings_brand = tk.Frame(settings_sidebar_inner, bg=self.theme["accent"], width=42, height=108)
        settings_brand.pack(anchor="center", pady=(2, 20))
        settings_brand.pack_propagate(False)

        for text in ("GEN", "VOC", "APP"):
            rail_item = tk.Label(
                settings_sidebar_inner,
                text=text,
                font=("Segoe UI", 8, "bold"),
                width=6,
                pady=10,
                bg=self.theme["sidebar"],
                fg=self.theme["muted"],
            )
            rail_item.pack(fill="x", pady=6)

        shell_main = tk.Frame(shell, bg=self.theme["shell"])
        shell_main.pack(side="left", fill="both", expand=True)

        header = tk.Frame(shell_main, bg=self.theme["shell"])
        header.pack(fill="x", padx=24, pady=(22, 14))

        header_copy = tk.Frame(header, bg=self.theme["shell"])
        header_copy.pack(side="left", fill="x", expand=True)

        heading = tk.Label(header_copy, text="Settings", font=("Segoe UI Semibold", 28), bg=self.theme["shell"], fg=self.theme["title"])
        heading.pack(anchor="w")

        subheading = tk.Label(
            header_copy,
            text="General and voice settings are saved locally. Gemini API access is read from .env.",
            font=("Segoe UI", 10),
            bg=self.theme["shell"],
            fg=self.theme["muted"],
        )
        subheading.pack(anchor="w", pady=(6, 0))

        settings_chip = tk.Label(
            header,
            text="Local Config",
            font=("Segoe UI", 9, "bold"),
            padx=12,
            pady=8,
            bg=self.theme["status_badge_bg"],
            fg=self.theme["status_badge_fg"],
        )
        settings_chip.pack(side="right", anchor="n")

        notebook_shell = tk.Frame(shell_main, bg=self.theme["panel"], highlightthickness=1, highlightbackground=self.theme["border"])
        notebook_shell.pack(fill="both", expand=True, padx=24, pady=(0, 18))

        notebook = ttk.Notebook(notebook_shell, style="Locus.TNotebook")
        notebook.pack(fill="both", expand=True, padx=18, pady=(18, 18))

        general_tab, general_content = self._build_scrollable_settings_tab(notebook)
        voice_tab, voice_content = self._build_scrollable_settings_tab(notebook)
        appearance_tab, appearance_content = self._build_scrollable_settings_tab(notebook)
        notebook.add(general_tab, text="General")
        notebook.add(voice_tab, text="Voice")
        notebook.add(appearance_tab, text="Appearance")

        api_key_var = tk.StringVar(value=load_gemini_api_key())
        model_var = tk.StringVar(value=current_settings["gemini_model"])
        language_choice_var = tk.StringVar(
            value=current_settings["language_code"] if current_settings["language_code"] in LANGUAGE_OPTIONS else "custom"
        )
        custom_language_var = tk.StringVar(
            value="" if current_settings["language_code"] in LANGUAGE_OPTIONS else current_settings["language_code"]
        )
        wake_word_vars = {
            key: tk.BooleanVar(value=key in current_settings["wake_words"]) for key in WAKE_WORD_PRESET_OPTIONS
        }
        custom_wake_words_var = tk.StringVar(
            value=", ".join(
                word for word in current_settings["wake_words"] if word not in WAKE_WORD_PRESET_OPTIONS
            )
        )
        input_device_var = tk.StringVar(
            value=self._get_audio_device_label(current_settings["microphone_device_id"], input_devices, "System default input")
        )
        output_device_var = tk.StringVar(
            value=self._get_audio_device_label(
                current_settings["output_audio_device_id"], output_devices, "System default output"
            )
        )
        theme_var = tk.StringVar(value=current_settings["theme"])
        animation_speed_var = tk.StringVar(value=current_settings["animation_speed"])

        error_labels["gemini_api_key"], gemini_status_label = self._build_setting_field(
            general_content,
            "Gemini API key",
            api_key_var,
            "Saved to .env as GEMINI_KEY and masked in this window.",
            show="*",
            include_status=True,
        )
        error_labels["gemini_model"] = self._build_setting_field(
            general_content,
            "Gemini model",
            model_var,
            "Example: gemini-flash-latest",
        )
        error_labels["language_code"] = self._build_language_selector(
            voice_content,
            language_choice_var,
            custom_language_var,
        )
        error_labels["wake_words"] = self._build_wake_word_selector(
            voice_content,
            wake_word_vars,
            custom_wake_words_var,
        )
        error_labels["microphone_device_id"] = self._build_microphone_selector(
            voice_content,
            "Input audio device",
            input_device_var,
            input_devices,
            "Select the microphone/input device or keep the system default.",
        )
        error_labels["output_audio_device_id"] = self._build_microphone_selector(
            voice_content,
            "Output audio device",
            output_device_var,
            output_devices,
            "Saved for future playback routing. Current app playback does not use this yet.",
        )
        error_labels["theme"] = self._build_theme_selector(appearance_content, theme_var)
        error_labels["animation_speed"] = self._build_speed_selector(appearance_content, animation_speed_var)

        button_row = tk.Frame(shell_main, bg=self.theme["shell"])
        button_row.pack(fill="x", padx=24, pady=(0, 22))

        def close_window():
            self.settings_window = None
            window.destroy()

        def clear_errors():
            for label in error_labels.values():
                label.config(text="")
            gemini_status_label.config(text="")

        def save_and_apply():
            clear_errors()
            effective_language_code = self._resolve_language_code(language_choice_var.get(), custom_language_var.get())
            effective_wake_words = self._resolve_wake_words(wake_word_vars, custom_wake_words_var.get())
            validation = validate_settings_input(
                {
                    "gemini_model": model_var.get(),
                    "language_code": effective_language_code,
                    "wake_words": effective_wake_words,
                    "microphone_device_id": self._get_audio_device_id(input_device_var.get(), input_devices),
                    "output_audio_device_id": self._get_audio_device_id(output_device_var.get(), output_devices),
                    "theme": theme_var.get(),
                    "animation_speed": animation_speed_var.get(),
                }
            )
            if not validation.is_valid:
                gemini_status_label.config(text="")
                for field_name, message in validation.errors.items():
                    label = error_labels.get(field_name)
                    if label:
                        label.config(text=message)
                return

            normalized_api_key = api_key_var.get().strip()
            gemini_validation = None
            if normalized_api_key:
                gemini_status_label.config(text="Checking Gemini access...", fg=self.theme["muted"])
                window.update_idletasks()
                gemini_validation = validate_gemini_configuration(normalized_api_key, model_var.get())
            else:
                gemini_status_label.config(text="Gemini key is empty. Gemini features will stay disabled.", fg=self.theme["warning"])

            try:
                save_gemini_api_key(normalized_api_key)
                saved_settings = save_settings(validation.settings)
                apply_settings(saved_settings)
                reload_gemini_client()
                self.apply_theme(config.THEME)
                self._refresh_dynamic_copy()
                self._start_bar_loop()

                if gemini_validation and gemini_validation.is_valid:
                    gemini_status_label.config(text="Gemini key and model validated.", fg=self.theme["success"])
                    messagebox.showinfo("Settings", "Settings saved.")
                elif gemini_validation:
                    gemini_status_label.config(text="Settings saved, but Gemini could not be verified.", fg=self.theme["warning"])
                    messagebox.showwarning(
                        "Settings",
                        "Settings were saved, but Gemini could not be verified.\n\n"
                        f"{gemini_validation.key_error or gemini_validation.model_error}",
                    )
                else:
                    messagebox.showinfo("Settings", "Settings saved. Gemini is disabled until you add an API key.")
                close_window()
            except OSError as exc:
                gemini_status_label.config(text="")
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
            padx=18,
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
            padx=18,
            pady=10,
        )
        save_btn.pack(side="right")

        window.protocol("WM_DELETE_WINDOW", close_window)

    def _build_scrollable_settings_tab(self, notebook):
        tab = tk.Frame(notebook, bg=self.theme["panel"])

        canvas = tk.Canvas(
            tab,
            bg=self.theme["panel"],
            highlightthickness=0,
            bd=0,
            relief="flat",
        )
        scrollbar = ttk.Scrollbar(tab, orient="vertical", command=canvas.yview)
        content = tk.Frame(canvas, bg=self.theme["panel"])

        content_window = canvas.create_window((0, 0), window=content, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        def sync_scrollregion(_event=None):
            canvas.configure(scrollregion=canvas.bbox("all"))

        def resize_content(event):
            canvas.itemconfigure(content_window, width=event.width)

        def on_mousewheel(event):
            if event.delta == 0:
                return
            canvas.yview_scroll(int(-event.delta / 120), "units")

        content.bind("<Configure>", sync_scrollregion)
        canvas.bind("<Configure>", resize_content)
        canvas.bind("<Enter>", lambda _event: canvas.bind_all("<MouseWheel>", on_mousewheel))
        canvas.bind("<Leave>", lambda _event: canvas.unbind_all("<MouseWheel>"))

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        return tab, content

    def _build_setting_field(self, parent, label_text, variable, note, show=None, include_status=False):
        block = tk.Frame(parent, bg=self.theme["panel_alt"], highlightthickness=1, highlightbackground=self.theme["border"])
        block.pack(fill="x", padx=18, pady=(18, 0))

        label = tk.Label(block, text=label_text, font=("Segoe UI", 10, "bold"), bg=self.theme["panel_alt"], fg=self.theme["title"])
        label.pack(anchor="w", padx=16, pady=(16, 6))

        entry = tk.Entry(
            block,
            textvariable=variable,
            relief="flat",
            font=("Segoe UI", 10),
            bg=self.theme["input_bg"],
            fg=self.theme["input_fg"],
            insertbackground=self.theme["input_fg"],
            show=show,
        )
        entry.pack(fill="x", padx=16, pady=(0, 10), ipady=10)

        note_label = tk.Label(block, text=note, font=("Segoe UI", 8), bg=self.theme["panel_alt"], fg=self.theme["muted"])
        note_label.pack(anchor="w", padx=16, pady=(0, 4))

        status_label = None
        if include_status:
            status_label = tk.Label(block, text="", font=("Segoe UI", 8, "bold"), bg=self.theme["panel_alt"], fg=self.theme["success"])
            status_label.pack(anchor="w", padx=16, pady=(0, 4))

        error_label = tk.Label(block, text="", font=("Segoe UI", 8, "bold"), bg=self.theme["panel_alt"], fg=self.theme["danger"])
        error_label.pack(anchor="w", padx=16, pady=(0, 16))
        if include_status:
            return error_label, status_label
        return error_label

    def _build_language_selector(self, parent, selection_var, custom_var):
        block = tk.Frame(parent, bg=self.theme["panel_alt"], highlightthickness=1, highlightbackground=self.theme["border"])
        block.pack(fill="x", padx=18, pady=(18, 0))

        label = tk.Label(block, text="Language", font=("Segoe UI", 10, "bold"), bg=self.theme["panel_alt"], fg=self.theme["title"])
        label.pack(anchor="w", padx=16, pady=(16, 6))

        values = [metadata["label"] for metadata in LANGUAGE_OPTIONS.values()] + ["Custom code"]
        display_by_value = {code: metadata["label"] for code, metadata in LANGUAGE_OPTIONS.items()}
        display_by_value["custom"] = "Custom code"
        value_by_display = {display: value for value, display in display_by_value.items()}
        selection_display = tk.StringVar(value=display_by_value.get(selection_var.get(), "Custom code"))

        def sync_language_choice(*_):
            selection_var.set(value_by_display.get(selection_display.get(), "custom"))
            custom_entry_state = "normal" if selection_var.get() == "custom" else "disabled"
            custom_entry.config(state=custom_entry_state)

        combo = ttk.Combobox(block, textvariable=selection_display, values=values, state="readonly", font=("Segoe UI", 10))
        combo.pack(fill="x", padx=16, pady=(0, 10), ipady=7)
        selection_display.trace_add("write", sync_language_choice)

        custom_entry = tk.Entry(
            block,
            textvariable=custom_var,
            relief="flat",
            font=("Segoe UI", 10),
            bg=self.theme["input_bg"],
            fg=self.theme["input_fg"],
            insertbackground=self.theme["input_fg"],
        )
        custom_entry.pack(fill="x", padx=16, pady=(0, 10), ipady=10)
        sync_language_choice()

        note_label = tk.Label(
            block,
            text="Pick a common language or enter a custom recognition code like en-US.",
            font=("Segoe UI", 8),
            bg=self.theme["panel_alt"],
            fg=self.theme["muted"],
        )
        note_label.pack(anchor="w", padx=16, pady=(0, 4))

        error_label = tk.Label(block, text="", font=("Segoe UI", 8, "bold"), bg=self.theme["panel_alt"], fg=self.theme["danger"])
        error_label.pack(anchor="w", padx=16, pady=(0, 16))
        return error_label

    def _build_wake_word_selector(self, parent, wake_word_vars, custom_var):
        block = tk.Frame(parent, bg=self.theme["panel_alt"], highlightthickness=1, highlightbackground=self.theme["border"])
        block.pack(fill="x", padx=18, pady=(18, 0))

        label = tk.Label(block, text="Wake words", font=("Segoe UI", 10, "bold"), bg=self.theme["panel_alt"], fg=self.theme["title"])
        label.pack(anchor="w", padx=16, pady=(16, 10))

        for key, metadata in WAKE_WORD_PRESET_OPTIONS.items():
            check = tk.Checkbutton(
                block,
                text=metadata["label"],
                variable=wake_word_vars[key],
                onvalue=True,
                offvalue=False,
                bg=self.theme["panel_alt"],
                fg=self.theme["text"],
                activebackground=self.theme["panel_alt"],
                activeforeground=self.theme["title"],
                selectcolor=self.theme["panel"],
                font=("Segoe UI", 10),
                anchor="w",
            )
            check.pack(anchor="w", padx=16, pady=(0, 4))

        custom_label = tk.Label(block, text="Custom wake words", font=("Segoe UI", 9, "bold"), bg=self.theme["panel_alt"], fg=self.theme["title"])
        custom_label.pack(anchor="w", padx=16, pady=(12, 4))

        custom_entry = tk.Entry(
            block,
            textvariable=custom_var,
            relief="flat",
            font=("Segoe UI", 10),
            bg=self.theme["input_bg"],
            fg=self.theme["input_fg"],
            insertbackground=self.theme["input_fg"],
        )
        custom_entry.pack(fill="x", padx=16, pady=(0, 10), ipady=10)

        note_label = tk.Label(
            block,
            text="Choose built-in wake words and optionally add your own words, separated by commas.",
            font=("Segoe UI", 8),
            bg=self.theme["panel_alt"],
            fg=self.theme["muted"],
        )
        note_label.pack(anchor="w", padx=16, pady=(0, 4))

        error_label = tk.Label(block, text="", font=("Segoe UI", 8, "bold"), bg=self.theme["panel_alt"], fg=self.theme["danger"])
        error_label.pack(anchor="w", padx=16, pady=(0, 16))
        return error_label

    def _build_microphone_selector(self, parent, label_text, variable, devices, note):
        block = tk.Frame(parent, bg=self.theme["panel_alt"], highlightthickness=1, highlightbackground=self.theme["border"])
        block.pack(fill="x", padx=18, pady=(18, 0))

        label = tk.Label(block, text=label_text, font=("Segoe UI", 10, "bold"), bg=self.theme["panel_alt"], fg=self.theme["title"])
        label.pack(anchor="w", padx=16, pady=(16, 6))

        values = [device["label"] for device in devices]
        combo = ttk.Combobox(block, textvariable=variable, values=values, state="readonly", font=("Segoe UI", 10))
        combo.pack(fill="x", padx=16, pady=(0, 10), ipady=7)

        note_label = tk.Label(block, text=note, font=("Segoe UI", 8), bg=self.theme["panel_alt"], fg=self.theme["muted"])
        note_label.pack(anchor="w", padx=16, pady=(0, 4))

        error_label = tk.Label(block, text="", font=("Segoe UI", 8, "bold"), bg=self.theme["panel_alt"], fg=self.theme["danger"])
        error_label.pack(anchor="w", padx=16, pady=(0, 16))
        return error_label

    def _append_stale_device(self, devices, selected_id, suffix):
        if not selected_id:
            return
        existing_ids = {device["id"] for device in devices}
        if selected_id in existing_ids:
            return
        devices.append({"id": selected_id, "label": f"{selected_id} ({suffix})"})

    def _get_audio_device_label(self, device_id, devices, default_label):
        for device in devices:
            if device["id"] == device_id:
                return device["label"]
        return default_label

    def _get_audio_device_id(self, label, devices):
        for device in devices:
            if device["label"] == label:
                return device["id"]
        return ""

    def _resolve_language_code(self, selection, custom_value):
        if selection == "custom":
            return custom_value.strip()
        return selection

    def _resolve_wake_words(self, wake_word_vars, custom_wake_words):
        selected_words = [key for key, variable in wake_word_vars.items() if variable.get()]
        custom_words = [word for word in custom_wake_words.split(",")] if custom_wake_words else []
        return selected_words + custom_words

    def _build_theme_selector(self, parent, variable):
        block = tk.Frame(parent, bg=self.theme["panel_alt"], highlightthickness=1, highlightbackground=self.theme["border"])
        block.pack(fill="x", padx=14, pady=(14, 0))

        label = tk.Label(block, text="UI style", font=("Segoe UI", 10, "bold"), bg=self.theme["panel_alt"], fg=self.theme["title"])
        label.pack(anchor="w", padx=14, pady=(14, 10))

        for key, metadata in THEME_OPTIONS.items():
            row = tk.Frame(block, bg=self.theme["panel_alt"])
            row.pack(fill="x", padx=14, pady=(0, 10))

            radio = tk.Radiobutton(
                row,
                text=metadata["label"],
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

            desc = tk.Label(
                row,
                text=metadata["description"],
                font=("Segoe UI", 8),
                bg=self.theme["panel_alt"],
                fg=self.theme["muted"],
            )
            desc.pack(anchor="w", padx=(24, 0))
        error_label = tk.Label(block, text="", font=("Segoe UI", 8, "bold"), bg=self.theme["panel_alt"], fg=self.theme["danger"])
        error_label.pack(anchor="w", padx=14, pady=(0, 14))
        return error_label

    def _build_speed_selector(self, parent, variable):
        block = tk.Frame(parent, bg=self.theme["panel_alt"], highlightthickness=1, highlightbackground=self.theme["border"])
        block.pack(fill="x", padx=14, pady=(14, 0))

        label = tk.Label(block, text="Animation speed", font=("Segoe UI", 10, "bold"), bg=self.theme["panel_alt"], fg=self.theme["title"])
        label.pack(anchor="w", padx=14, pady=(14, 10))

        options = tk.Frame(block, bg=self.theme["panel_alt"])
        options.pack(fill="x", padx=14, pady=(0, 14))

        for key, metadata in ANIMATION_SPEED_OPTIONS.items():
            radio = tk.Radiobutton(
                options,
                text=metadata["label"],
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
        error_label = tk.Label(block, text="", font=("Segoe UI", 8, "bold"), bg=self.theme["panel_alt"], fg=self.theme["danger"])
        error_label.pack(anchor="w", padx=14, pady=(0, 14))
        return error_label
