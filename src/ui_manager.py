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


# ---------------------------------------------------------------------------
# Theme definitions  (matches design reference palette exactly)
# ---------------------------------------------------------------------------
THEMES = {
    "glass_green": {
        "root_bg":          "#0a1a0e",
        "shell":            "#0d1f12",
        "shell_border":     "#1a4d2e",
        "sidebar":          "#091510",
        "panel":            "#0e2016",
        "panel_alt":        "#132819",
        "border":           "#1a4d2e",
        "title":            "#d8f5e5",
        "text":             "#d8f5e5",
        "muted":            "#5a8a6a",
        "accent":           "#00e87a",
        "accent_soft":      "#183A24",
        "accent_alt":       "#89F59E",
        "accent_dim":       "#0d2e18",
        "success":          "#6AFF8B",
        "warning":          "#DAF86A",
        "danger":           "#FF7B87",
        "button_bg":        "#00e87a",
        "button_fg":        "#021208",
        "button_active":    "#1df08c",
        "secondary_bg":     "#132819",
        "secondary_fg":     "#d8f5e5",
        "secondary_active": "#1a3521",
        "chip_bg":          "#0d2218",
        "chip_fg":          "#00e87a",
        "status_badge_bg":  "#0d2e18",
        "status_badge_fg":  "#00e87a",
        "bar_off":          "#1a3521",
        "bar_on":           "#00e87a",
        "canvas_bg":        "#0b1a10",
        "input_bg":         "#091510",
        "input_fg":         "#d8f5e5",
        "search_bg":        "#0b1910",
        "search_fg":        "#d8f5e5",
        "sidebar_accent":   "#00ff7f",
    },
    "dark": {
        "root_bg":          "#0c1017",
        "shell":            "#11151c",
        "shell_border":     "#1e2a3a",
        "sidebar":          "#0c1017",
        "panel":            "#141a23",
        "panel_alt":        "#1a2233",
        "border":           "#1e2a3a",
        "title":            "#e8eaf0",
        "text":             "#e3eaf4",
        "muted":            "#5a6478",
        "accent":           "#22c55e",
        "accent_soft":      "#173324",
        "accent_alt":       "#38BDF8",
        "accent_dim":       "#162a1f",
        "success":          "#4ADE80",
        "warning":          "#F59E0B",
        "danger":           "#F87171",
        "button_bg":        "#22c55e",
        "button_fg":        "#030b05",
        "button_active":    "#2ed56a",
        "secondary_bg":     "#1a2233",
        "secondary_fg":     "#e2e8f0",
        "secondary_active": "#222d40",
        "chip_bg":          "#14202d",
        "chip_fg":          "#22c55e",
        "status_badge_bg":  "#122a1c",
        "status_badge_fg":  "#22c55e",
        "bar_off":          "#1e2a3a",
        "bar_on":           "#22c55e",
        "canvas_bg":        "#0f1520",
        "input_bg":         "#0c1017",
        "input_fg":         "#e2e8f0",
        "search_bg":        "#0e131c",
        "search_fg":        "#d8e2ee",
        "sidebar_accent":   "#22c55e",
    },
    "light": {
        "root_bg":          "#e8eef0",
        "shell":            "#f3f7f4",
        "shell_border":     "#d0dcd8",
        "sidebar":          "#ffffff",
        "panel":            "#ffffff",
        "panel_alt":        "#f3f7fa",
        "border":           "#d7e2e9",
        "title":            "#111827",
        "text":             "#2f3e4f",
        "muted":            "#6b7280",
        "accent":           "#16a34a",
        "accent_soft":      "#dcf6e5",
        "accent_alt":       "#38BDF8",
        "accent_dim":       "#e7f6ec",
        "success":          "#16a34a",
        "warning":          "#D97706",
        "danger":           "#DC2626",
        "button_bg":        "#16a34a",
        "button_fg":        "#ffffff",
        "button_active":    "#1db356",
        "secondary_bg":     "#e2e8f0",
        "secondary_fg":     "#334155",
        "secondary_active": "#d7e0e9",
        "chip_bg":          "#eef5f0",
        "chip_fg":          "#16a34a",
        "status_badge_bg":  "#e8f5ec",
        "status_badge_fg":  "#16a34a",
        "bar_off":          "#dde5ee",
        "bar_on":           "#16a34a",
        "canvas_bg":        "#f7fafc",
        "input_bg":         "#ffffff",
        "input_fg":         "#1e293b",
        "search_bg":        "#f7faf8",
        "search_fg":        "#334155",
        "sidebar_accent":   "#16a34a",
    },
    "colorful": {
        "root_bg":          "#0e0620",
        "shell":            "#100820",
        "shell_border":     "#3d2060",
        "sidebar":          "#0e0620",
        "panel":            "#1c1032",
        "panel_alt":        "#241840",
        "border":           "#3d2060",
        "title":            "#f0eaff",
        "text":             "#f0eaff",
        "muted":            "#8b7aab",
        "accent":           "#f97316",
        "accent_soft":      "#472514",
        "accent_alt":       "#F472B6",
        "accent_dim":       "#2e1808",
        "success":          "#4ADE80",
        "warning":          "#FACC15",
        "danger":           "#FB7185",
        "button_bg":        "#f97316",
        "button_fg":        "#1a0820",
        "button_active":    "#ff8b37",
        "secondary_bg":     "#241840",
        "secondary_fg":     "#f8e9ff",
        "secondary_active": "#2e2050",
        "chip_bg":          "#241640",
        "chip_fg":          "#f97316",
        "status_badge_bg":  "#2e1808",
        "status_badge_fg":  "#f97316",
        "bar_off":          "#3d2060",
        "bar_on":           "#f97316",
        "canvas_bg":        "#0e0820",
        "input_bg":         "#1c1032",
        "input_fg":         "#f6edff",
        "search_bg":        "#180e30",
        "search_fg":        "#f3e8ff",
        "sidebar_accent":   "#f97316",
    },
    "nyan": {
        "root_bg":          "#08000f",
        "shell":            "#0d0018",
        "shell_border":     "#3a0050",
        "sidebar":          "#0a0015",
        "panel":            "#1a0028",
        "panel_alt":        "#220035",
        "border":           "#3a0050",
        "title":            "#ffe8f8",
        "text":             "#ffe8f8",
        "muted":            "#9b6aaa",
        "accent":           "#ff2d78",
        "accent_soft":      "#3d0020",
        "accent_alt":       "#00dcff",
        "accent_dim":       "#2a0018",
        "success":          "#4ADE80",
        "warning":          "#FACC15",
        "danger":           "#FF7B87",
        "button_bg":        "#ff2d78",
        "button_fg":        "#1a0020",
        "button_active":    "#ff5a96",
        "secondary_bg":     "#220035",
        "secondary_fg":     "#ffe8f8",
        "secondary_active": "#2e0045",
        "chip_bg":          "#200030",
        "chip_fg":          "#ff6eb4",
        "status_badge_bg":  "#2a0018",
        "status_badge_fg":  "#ff6eb4",
        "bar_off":          "#3a0050",
        "bar_on":           "#ff2d78",
        "canvas_bg":        "#080010",
        "input_bg":         "#150020",
        "input_fg":         "#ffe8f8",
        "search_bg":        "#100018",
        "search_fg":        "#ffe8f8",
        "sidebar_accent":   "#ff2d78",
    },
}

ANIMATION_SPEEDS = {
    "slow":   {"delay": 80,  "smoothing": 0.15},
    "normal": {"delay": 55,  "smoothing": 0.22},
    "fast":   {"delay": 35,  "smoothing": 0.30},
}

STATUS_TONES = {
    "idle":      "muted",
    "listening": "accent",
    "thinking":  "accent_alt",
    "prompt":    "warning",
    "success":   "success",
    "error":     "danger",
}

# Theme switcher order + short labels (matches design reference)
THEME_SWITCH_ORDER = ("glass_green", "dark", "light", "colorful", "nyan")
THEME_SHORT_LABELS = {
    "glass_green": "Glass",
    "dark":        "Dark",
    "light":       "Light",
    "colorful":    "Color",
    "nyan":        "Nyan 🐱",
}


class LocusUI:
    def __init__(self, root):
        self.root = root
        self.current_raw_img = None
        self.animation_id = None
        self.manual_action = None
        self.settings_window = None
        self.current_theme_name = config.THEME if config.THEME in THEMES else "glass_green"
        self.theme = THEMES[self.current_theme_name]

        self.mic_state = "idle"
        self.mic_level = 0.0
        self.smoothed_level = 0.0
        self.bar_loop_id = None
        self.bar_tick = 0
        self.conversation_messages = []

        # Pulsing dot animation state
        self._pulse_state = False
        self._pulse_id = None

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
        self._start_pulse_animation()
        self.root.bind("<Configure>", self._handle_resize)

    # ------------------------------------------------------------------
    # Style configuration
    # ------------------------------------------------------------------
    def _configure_styles(self):
        self.ttk_style = ttk.Style()
        try:
            self.ttk_style.theme_use("clam")
        except tk.TclError:
            pass

    # ------------------------------------------------------------------
    # Layout builders
    # ------------------------------------------------------------------
    def _build_layout(self):
        self._build_shell()
        self._build_sidebar()
        self._build_top_bar()
        self._build_content_area()
        self._build_dashboard()
        self._build_assistant_panel()
        self._build_voice_panel()
        self._build_conversation_panel()
        self._build_session_panel()

    def _build_shell(self):
        """Outer shell: root → main_frame → shell_frame (border) → body_frame (horizontal)."""
        self.main_frame = tk.Frame(self.root, bd=0, highlightthickness=0)
        self.main_frame.pack(fill="both", expand=True)

        self.shell_frame = tk.Frame(self.main_frame, bd=0, highlightthickness=1)
        self.shell_frame.pack(fill="both", expand=True, padx=0, pady=0)

        # body_frame holds sidebar (left) + main_column (right)
        self.body_frame = tk.Frame(self.shell_frame, bd=0, highlightthickness=0)
        self.body_frame.pack(fill="both", expand=True)

        # main column holds top bar + content area
        self.main_column = tk.Frame(self.body_frame, bd=0, highlightthickness=0)
        self.main_column.pack(side="left", fill="both", expand=True)

    def _build_sidebar(self):
        """Slim 64-px icon rail with 4-px left accent strip and pulsing status dot."""
        # Outer rail container
        self.rail_frame = tk.Frame(
            self.body_frame,
            bd=0, highlightthickness=0,
            width=64,
        )
        self.rail_frame.pack(side="left", fill="y", before=self.main_column)
        self.rail_frame.pack_propagate(False)

        # 4-px accent strip on the very left edge
        self.accent_strip = tk.Frame(self.rail_frame, width=4, bd=0, highlightthickness=0)
        self.accent_strip.pack(side="left", fill="y")

        # Inner content column
        self.rail_inner = tk.Frame(self.rail_frame, bd=0, highlightthickness=0)
        self.rail_inner.pack(side="left", fill="both", expand=True)

        # Right-side separator line
        self.rail_sep = tk.Frame(self.rail_inner, width=1, bd=0, highlightthickness=0)
        self.rail_sep.pack(side="right", fill="y")

        # Pulsing status dot
        self.pulse_canvas = tk.Canvas(
            self.rail_inner,
            width=8, height=8,
            bd=0, highlightthickness=0,
        )
        self.pulse_canvas.pack(pady=(20, 18))

        # Nav items
        self.rail_nav = tk.Frame(self.rail_inner, bd=0, highlightthickness=0)
        self.rail_nav.pack(fill="x", expand=False)

        self.rail_items = []
        for icon_text, label_text, is_active in (
            ("⌂", "HOME", True),
            ("◉", "MIC",  False),
            ("✦", "CHAT", False),
            ("⚙", "SET",  False),
        ):
            item_frame = tk.Frame(
                self.rail_nav,
                bd=0, highlightthickness=0,
                width=56, height=56,
                cursor="hand2",
            )
            item_frame.pack(pady=2)
            item_frame.pack_propagate(False)

            icon = tk.Label(
                item_frame,
                text=icon_text,
                font=("Segoe UI Symbol", 14),
                anchor="center",
                cursor="hand2",
            )
            icon.pack(pady=(10, 0))

            label = tk.Label(
                item_frame,
                text=label_text,
                font=("Segoe UI", 7, "bold"),
                anchor="center",
                cursor="hand2",
            )
            label.pack(pady=(0, 8))

            self.rail_items.append({
                "frame": item_frame,
                "icon":  icon,
                "label": label,
                "active": is_active,
            })

        # Footer voice item
        self.rail_footer_frame = tk.Frame(
            self.rail_inner, bd=0, highlightthickness=0, cursor="hand2",
        )
        self.rail_footer_frame.pack(side="bottom", pady=(0, 18))

        self.rail_footer_icon = tk.Label(
            self.rail_footer_frame,
            text="◌",
            font=("Segoe UI Symbol", 14),
            anchor="center",
        )
        self.rail_footer_icon.pack(pady=(8, 0))

        self.rail_footer_label = tk.Label(
            self.rail_footer_frame,
            text="VOICE",
            font=("Segoe UI", 7, "bold"),
        )
        self.rail_footer_label.pack(pady=(0, 8))

    def _build_top_bar(self):
        """Top bar: brand | search | theme-pill | status badge."""
        self.top_bar = tk.Frame(self.main_column, bd=0, highlightthickness=1)
        self.top_bar.pack(fill="x")

        inner = tk.Frame(self.top_bar, bd=0, highlightthickness=0)
        inner.pack(fill="x", padx=24, pady=16)

        # Brand block (left)
        self.brand_block = tk.Frame(inner, bd=0, highlightthickness=0)
        self.brand_block.pack(side="left", fill="x", expand=True)

        self.title_label = tk.Label(
            self.brand_block,
            text="Locus AI",
            font=("Segoe UI Semibold", 22),
            anchor="w",
        )
        self.title_label.pack(anchor="w")

        self.subtitle_label = tk.Label(
            self.brand_block,
            text="Voice assistant with local intents, Gemini fallback, and reactive cat states.",
            font=("Segoe UI", 10),
            anchor="w",
        )
        self.subtitle_label.pack(anchor="w", pady=(2, 0))

        # Utility block (right)
        self.utility_block = tk.Frame(inner, bd=0, highlightthickness=0)
        self.utility_block.pack(side="right", anchor="center")

        # Search box
        self.search_shell = tk.Frame(
            self.utility_block,
            bd=0, highlightthickness=1,
            padx=0, pady=0,
        )
        self.search_shell.pack(side="left", padx=(0, 12))

        self.search_icon = tk.Label(
            self.search_shell,
            text="⌕",
            font=("Segoe UI", 11),
            padx=8, pady=0,
        )
        self.search_icon.pack(side="left")

        self.search_entry = tk.Entry(
            self.search_shell,
            relief="flat",
            font=("Segoe UI", 10),
            width=14,
            bd=0,
        )
        self.search_entry.pack(side="left", ipady=7, padx=(0, 8))

        # Theme pill switcher
        self.theme_switcher = tk.Frame(
            self.utility_block,
            bd=0, highlightthickness=1,
        )
        self.theme_switcher.pack(side="left", padx=(0, 12))

        self.theme_switcher_inner = tk.Frame(self.theme_switcher, bd=0, highlightthickness=0)
        self.theme_switcher_inner.pack(padx=4, pady=4)

        self.theme_buttons = {}
        for theme_name in THEME_SWITCH_ORDER:
            button = tk.Button(
                self.theme_switcher_inner,
                text=THEME_SHORT_LABELS[theme_name],
                font=("Segoe UI", 8, "bold"),
                relief="flat",
                cursor="hand2",
                command=lambda tn=theme_name: self.apply_theme(tn),
                padx=8,
                pady=4,
                bd=0,
            )
            button.pack(side="left", padx=(0, 2))
            self.theme_buttons[theme_name] = button

        # Status badge (pulsing dot + label)
        self.status_badge_frame = tk.Frame(
            self.utility_block,
            bd=0, highlightthickness=1,
        )
        self.status_badge_frame.pack(side="left")

        badge_inner = tk.Frame(self.status_badge_frame, bd=0, highlightthickness=0)
        badge_inner.pack(padx=10, pady=6)

        self.top_pulse_canvas = tk.Canvas(
            badge_inner,
            width=6, height=6,
            bd=0, highlightthickness=0,
        )
        self.top_pulse_canvas.pack(side="left", padx=(0, 6))

        self.top_status_chip = tk.Label(
            badge_inner,
            text="Idle",
            font=("Segoe UI", 9, "bold"),
        )
        self.top_status_chip.pack(side="left")

    def _build_content_area(self):
        self.content_frame = tk.Frame(self.main_column, bd=0, highlightthickness=0)
        self.content_frame.pack(fill="both", expand=True, padx=20, pady=(16, 20))

    def _build_dashboard(self):
        self.dashboard_frame = tk.Frame(self.content_frame, bd=0, highlightthickness=0)
        self.dashboard_frame.pack(fill="both", expand=True)
        self.dashboard_frame.grid_columnconfigure(0, weight=3)
        self.dashboard_frame.grid_columnconfigure(1, weight=2)
        self.dashboard_frame.grid_rowconfigure(0, weight=2)
        self.dashboard_frame.grid_rowconfigure(1, weight=2)

    def _build_assistant_panel(self):
        self.hero_card = self._create_card(self.dashboard_frame)
        self.hero_card.grid(row=0, column=0, sticky="nsew", padx=(0, 12), pady=(0, 12))

        # Card header
        self.hero_header = tk.Frame(self.hero_card, bd=0, highlightthickness=0)
        self.hero_header.pack(fill="x", padx=16, pady=(14, 10))

        self.hero_title = tk.Label(
            self.hero_header,
            text="Assistant",
            font=("Segoe UI Semibold", 13),
            anchor="w",
        )
        self.hero_title.pack(side="left")

        self.hero_hint = tk.Label(
            self.hero_header,
            text="Click the cat to wake it",
            font=("Segoe UI", 9),
            padx=0, pady=0,
            anchor="e",
            cursor="hand2",
        )
        self.hero_hint.pack(side="right")

        # Card body
        self.hero_body = tk.Frame(self.hero_card, bd=0, highlightthickness=0)
        self.hero_body.pack(fill="both", expand=True, padx=16, pady=(0, 16))
        self.hero_body.grid_columnconfigure(0, weight=0)
        self.hero_body.grid_columnconfigure(1, weight=1)

        # Cat image frame (140px wide)
        self.image_frame = tk.Frame(
            self.hero_body,
            bd=0, highlightthickness=0,
            width=140,
        )
        self.image_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 14))
        self.image_frame.grid_propagate(False)

        self.image_label = tk.Label(self.image_frame, cursor="hand2", bd=0, highlightthickness=0)
        self.image_label.pack(fill="both", expand=True)

        # Overlay (gradient-like dark strip at bottom of image)
        self.hero_overlay = tk.Frame(self.image_frame, bd=0, highlightthickness=0)
        self.hero_overlay.place(relx=0, rely=1.0, relwidth=1.0, anchor="sw")

        self.hero_overlay_title = tk.Label(
            self.hero_overlay,
            text="Go ahead",
            font=("Segoe UI Semibold", 13),
            anchor="w",
            padx=10, pady=4,
        )
        self.hero_overlay_title.pack(fill="x")

        self.hero_caption = tk.Label(
            self.hero_overlay,
            text="Wake words: " + ", ".join(config.WAKE_WORDS),
            font=("Segoe UI", 8),
            anchor="w",
            justify="left",
            padx=10, pady=0,
        )
        self.hero_caption.pack(fill="x", pady=(0, 6))

        # Control deck (right side)
        self.hero_side = tk.Frame(self.hero_body, bd=0, highlightthickness=0)
        self.hero_side.grid(row=0, column=1, sticky="nsew")
        self.hero_side.grid_rowconfigure(5, weight=1)

        self.hero_side_title = tk.Label(
            self.hero_side,
            text="Control Deck",
            font=("Segoe UI Semibold", 13),
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
        self.hero_side_copy.pack(fill="x", pady=(4, 12))

        self.listen_btn = tk.Button(
            self.hero_side,
            text="Listen",
            font=("Segoe UI", 11, "bold"),
            relief="flat",
            command=self.trigger_manual_action,
            cursor="hand2",
            padx=18,
            pady=12,
            bd=0,
        )
        self.listen_btn.pack(fill="x", pady=(0, 8))

        self.settings_btn = tk.Button(
            self.hero_side,
            text="Settings",
            font=("Segoe UI", 10),
            relief="flat",
            command=self.open_settings_window,
            cursor="hand2",
            padx=18,
            pady=10,
            bd=0,
        )
        self.settings_btn.pack(fill="x", pady=(0, 12))

        # Quick stats with glowing dot indicator
        self.quick_stats = []
        for label_text in ("Wake Word Ready", "Manual Trigger Enabled", "Gemini Standby"):
            row = tk.Frame(self.hero_side, bd=0, highlightthickness=0)
            row.pack(fill="x", pady=(0, 4))

            dot = tk.Canvas(row, width=7, height=7, bd=0, highlightthickness=0)
            dot.pack(side="left", padx=(0, 6))

            chip = tk.Label(
                row,
                text=label_text,
                font=("Segoe UI", 9),
                anchor="w",
            )
            chip.pack(side="left", fill="x")
            self.quick_stats.append({"dot": dot, "label": chip, "row": row})

    def _build_voice_panel(self):
        self.mic_card = self._create_card(self.dashboard_frame)
        self.mic_card.grid(row=0, column=1, sticky="nsew", pady=(0, 12))

        # Card header
        self.mic_header = tk.Frame(self.mic_card, bd=0, highlightthickness=0)
        self.mic_header.pack(fill="x", padx=16, pady=(14, 8))

        self.status_text = tk.Label(
            self.mic_header,
            text="Say 'Locus'",
            font=("Segoe UI Semibold", 13),
            anchor="w",
        )
        self.status_text.pack(side="left")

        self.mic_mode_label = tk.Label(
            self.mic_header,
            text="Idle",
            font=("Segoe UI", 9, "bold"),
            padx=10, pady=4,
        )
        self.mic_mode_label.pack(side="right")

        # Sub-description
        self.voice_intro = tk.Label(
            self.mic_card,
            text="Left-click the cat or wait for the wake word.",
            font=("Segoe UI", 9),
            anchor="w",
            justify="left",
        )
        self.voice_intro.pack(fill="x", padx=16, pady=(0, 10))

        # Voice activity row
        self.voice_meta = tk.Frame(self.mic_card, bd=0, highlightthickness=0)
        self.voice_meta.pack(fill="x", padx=16, pady=(0, 4))

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
        )
        self.voice_meta_state.pack(side="right")

        self.status_subtext = tk.Label(
            self.mic_card,
            text="Waiting for activation",
            font=("Segoe UI", 9),
            anchor="w",
            justify="left",
        )
        self.status_subtext.pack(fill="x", padx=16, pady=(0, 10))

        # Main waveform canvas
        self.mic_canvas = tk.Canvas(self.mic_card, height=72, bd=0, highlightthickness=0)
        self.mic_canvas.pack(fill="x", expand=False, padx=16, pady=(0, 0))

        # Separator line above history strip
        self.voice_sep = tk.Frame(self.mic_card, height=1, bd=0, highlightthickness=0)
        self.voice_sep.pack(fill="x", padx=16, pady=(8, 0))

        # History mini-bars
        self.history_canvas = tk.Canvas(self.mic_card, height=36, bd=0, highlightthickness=0)
        self.history_canvas.pack(fill="x", expand=False, padx=16, pady=(4, 16))

    def _build_conversation_panel(self):
        self.transcript_card = self._create_card(self.dashboard_frame)
        self.transcript_card.grid(row=1, column=0, sticky="nsew", padx=(0, 12))

        # Card header
        self.transcript_header = tk.Frame(self.transcript_card, bd=0, highlightthickness=0)
        self.transcript_header.pack(fill="x", padx=16, pady=(14, 10))

        self.transcript_title = tk.Label(
            self.transcript_header,
            text="Conversation",
            font=("Segoe UI Semibold", 13),
            anchor="w",
        )
        self.transcript_title.pack(side="left")

        self.transcript_chip = tk.Label(
            self.transcript_header,
            text="Live Preview",
            font=("Segoe UI", 9),
            padx=0, pady=0,
        )
        self.transcript_chip.pack(side="right")

        # Scrollable message area
        self.transcript_canvas = tk.Canvas(self.transcript_card, bd=0, highlightthickness=0)
        self.transcript_canvas.pack(fill="both", expand=True, padx=(14, 4), pady=(0, 16), side="left")

        self.transcript_scrollbar = ttk.Scrollbar(
            self.transcript_card,
            orient="vertical",
            command=self.transcript_canvas.yview,
        )
        self.transcript_scrollbar.pack(fill="y", side="right", padx=(0, 10), pady=(0, 16))
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

        # Card header
        self.control_header = tk.Frame(self.control_card, bd=0, highlightthickness=0)
        self.control_header.pack(fill="x", padx=16, pady=(14, 10))

        self.control_title = tk.Label(
            self.control_header,
            text="Session Summary",
            font=("Segoe UI Semibold", 13),
            anchor="w",
        )
        self.control_title.pack(side="left")

        self.control_chip = tk.Label(
            self.control_header,
            text="Dashboard",
            font=("Segoe UI", 9),
        )
        self.control_chip.pack(side="right")

        # Session rows with separator-line style
        self.summary_rows = []
        rows_data = (
            ("MODEL",       config.MODEL_NAME),
            ("WAKE WORDS",  ", ".join(config.WAKE_WORDS)),
            ("INTERACTION", "Waiting for the next command."),
            ("AUDIO",       "Input: system default"),
        )
        for i, (heading, detail) in enumerate(rows_data):
            # Separator line above each row (except the first)
            if i > 0:
                sep = tk.Frame(self.control_card, height=1, bd=0, highlightthickness=0)
                sep.pack(fill="x", padx=16)
                # Keep reference for theming
                self.summary_rows[-1]["sep_after"] = sep

            row_frame = tk.Frame(self.control_card, bd=0, highlightthickness=0)
            row_frame.pack(fill="x", padx=16, pady=(8, 4))

            title = tk.Label(
                row_frame,
                text=heading,
                font=("Segoe UI", 8, "bold"),
                anchor="w",
            )
            title.pack(fill="x")

            copy = tk.Label(
                row_frame,
                text=detail,
                font=("Segoe UI", 10),
                justify="left",
                anchor="w",
                wraplength=300,
            )
            copy.pack(fill="x", pady=(2, 0))

            self.summary_rows.append({
                "frame": row_frame,
                "title": title,
                "copy":  copy,
                "sep_after": None,
            })

        self.footer_note = None

    # ------------------------------------------------------------------
    # Card factory
    # ------------------------------------------------------------------
    def _create_card(self, parent):
        return tk.Frame(parent, bd=0, highlightthickness=1)

    # ------------------------------------------------------------------
    # Button colour helper
    # ------------------------------------------------------------------
    def _set_button_colors(self, button, bg, fg, active_bg):
        button.config(
            bg=bg,
            fg=fg,
            activebackground=active_bg,
            activeforeground=fg,
            highlightthickness=0,
            bd=0,
        )

    # ------------------------------------------------------------------
    # Pulsing dot animation
    # ------------------------------------------------------------------
    def _start_pulse_animation(self):
        if self._pulse_id:
            self.root.after_cancel(self._pulse_id)
        self._pulse_state = not self._pulse_state
        self._draw_pulse_dots()
        self._pulse_id = self.root.after(700, self._start_pulse_animation)

    def _draw_pulse_dots(self):
        """Redraw the sidebar dot and top-bar badge dot."""
        is_active = self.mic_state != "idle"
        accent = self.theme["accent"]
        muted  = self.theme["muted"]

        # Sidebar dot
        self.pulse_canvas.config(bg=self.theme["sidebar"])
        self.pulse_canvas.delete("all")
        colour = accent if (is_active or self._pulse_state) else muted
        self.pulse_canvas.create_oval(0, 0, 8, 8, fill=colour, outline="")

        # Top bar badge dot
        self.top_pulse_canvas.config(bg=self.theme["status_badge_bg"])
        self.top_pulse_canvas.delete("all")
        top_colour = self.theme["status_badge_fg"] if (is_active or self._pulse_state) else muted
        self.top_pulse_canvas.create_oval(0, 0, 6, 6, fill=top_colour, outline="")

    # ------------------------------------------------------------------
    # Quick-stat dots
    # ------------------------------------------------------------------
    def _draw_quick_stat_dots(self):
        for stat in self.quick_stats:
            dot_canvas = stat["dot"]
            dot_canvas.config(bg=self.theme["panel"])
            dot_canvas.delete("all")
            dot_canvas.create_oval(0, 0, 7, 7, fill=self.theme["accent"], outline="")

    # ------------------------------------------------------------------
    # Theme application
    # ------------------------------------------------------------------
    def _set_theme_switch_button_colors(self):
        for theme_name, button in self.theme_buttons.items():
            is_selected = (theme_name == self.current_theme_name)
            bg        = self.theme["button_bg"]        if is_selected else self.theme["search_bg"]
            fg        = self.theme["button_fg"]        if is_selected else self.theme["muted"]
            active_bg = self.theme["button_active"]    if is_selected else self.theme["secondary_active"]
            self._set_button_colors(button, bg, fg, active_bg)
            button.config(bg=bg, fg=fg, activebackground=active_bg, activeforeground=fg)

    def _apply_sidebar_item_styles(self):
        for item in self.rail_items:
            is_active = item["active"]
            frame_bg  = self.theme["accent_dim"] if is_active else self.theme["sidebar"]
            text_fg   = self.theme["accent"]     if is_active else self.theme["muted"]

            item["frame"].config(bg=frame_bg)
            item["icon"].config(bg=frame_bg, fg=text_fg)
            item["label"].config(bg=frame_bg, fg=text_fg)

        self.rail_footer_frame.config(bg=self.theme["sidebar"])
        self.rail_footer_icon.config(bg=self.theme["sidebar"], fg=self.theme["muted"])
        self.rail_footer_label.config(bg=self.theme["sidebar"], fg=self.theme["muted"])

    def apply_theme(self, theme_name=None):
        if theme_name:
            self.current_theme_name = theme_name
        self.theme = THEMES.get(self.current_theme_name, THEMES["glass_green"])
        t = self.theme  # shorthand

        # Root & shell
        self.root.config(bg=t["root_bg"])
        self.main_frame.config(bg=t["root_bg"])
        self.shell_frame.config(bg=t["shell"], highlightbackground=t["shell_border"])
        self.body_frame.config(bg=t["shell"])
        self.main_column.config(bg=t["shell"])

        # Top bar
        self.top_bar.config(bg=t["shell"], highlightbackground=t["border"])
        for w in (self.brand_block, self.utility_block):
            w.config(bg=t["shell"])

        self.title_label.config(bg=t["shell"], fg=t["title"])
        self.subtitle_label.config(bg=t["shell"], fg=t["muted"])

        # Search box
        self.search_shell.config(
            bg=t["search_bg"],
            highlightbackground=t["border"],
        )
        self.search_icon.config(bg=t["search_bg"], fg=t["muted"])
        self.search_entry.config(bg=t["search_bg"], fg=t["search_fg"],
                                  insertbackground=t["search_fg"])

        # Theme pill
        self.theme_switcher.config(bg=t["search_bg"], highlightbackground=t["border"])
        self.theme_switcher_inner.config(bg=t["search_bg"])
        self._set_theme_switch_button_colors()

        # Status badge
        self.status_badge_frame.config(
            bg=t["status_badge_bg"],
            highlightbackground=t["border"],
        )
        self.top_status_chip.config(
            bg=t["status_badge_bg"],
            fg=t["status_badge_fg"],
        )
        badge_inner = self.top_pulse_canvas.master
        badge_inner.config(bg=t["status_badge_bg"])

        # Sidebar
        self.rail_frame.config(bg=t["sidebar"])
        self.accent_strip.config(bg=t["sidebar_accent"])
        self.rail_inner.config(bg=t["sidebar"])
        self.rail_sep.config(bg=t["border"])
        self.pulse_canvas.config(bg=t["sidebar"])
        self.rail_nav.config(bg=t["sidebar"])
        self._apply_sidebar_item_styles()

        # Content
        self.content_frame.config(bg=t["shell"])
        self.dashboard_frame.config(bg=t["shell"])

        # Panel cards
        for card in (self.hero_card, self.mic_card, self.transcript_card, self.control_card):
            card.config(bg=t["panel"], highlightbackground=t["border"])

        # Assistant panel
        for w in (self.hero_header, self.hero_body, self.hero_side):
            w.config(bg=t["panel"])
        self.hero_title.config(bg=t["panel"], fg=t["title"])
        self.hero_hint.config(bg=t["panel"], fg=t["chip_fg"])
        self.image_frame.config(bg=t["panel"])
        self.image_label.config(bg=t["panel"])
        self.hero_overlay.config(bg=t["accent_dim"])
        self.hero_overlay_title.config(bg=t["accent_dim"], fg=t["accent"])
        self.hero_caption.config(bg=t["accent_dim"], fg=t["text"])
        self.hero_side_title.config(bg=t["panel"], fg=t["title"])
        self.hero_side_copy.config(bg=t["panel"], fg=t["muted"])

        for stat in self.quick_stats:
            stat["row"].config(bg=t["panel"])
            stat["label"].config(bg=t["panel"], fg=t["accent"])
        self._draw_quick_stat_dots()

        self._set_button_colors(
            self.listen_btn,
            t["button_bg"], t["button_fg"], t["button_active"],
        )
        self._set_button_colors(
            self.settings_btn,
            t["secondary_bg"], t["secondary_fg"], t["secondary_active"],
        )

        # Voice panel
        status_color = t[STATUS_TONES.get(self.mic_state, "muted")]
        self.mic_header.config(bg=t["panel"])
        self.status_text.config(bg=t["panel"], fg=status_color)
        self.mic_mode_label.config(bg=t["chip_bg"], fg=t["chip_fg"])
        self.voice_intro.config(bg=t["panel"], fg=t["muted"])
        self.voice_meta.config(bg=t["panel"])
        self.voice_meta_label.config(bg=t["panel"], fg=t["title"])
        self.voice_meta_state.config(bg=t["chip_bg"], fg=t["chip_fg"])
        self.status_subtext.config(bg=t["panel"], fg=t["muted"])
        self.voice_sep.config(bg=t["border"])
        self.mic_canvas.config(bg=t["canvas_bg"])
        self.history_canvas.config(bg=t["canvas_bg"])

        # Conversation panel
        self.transcript_header.config(bg=t["panel"])
        self.transcript_title.config(bg=t["panel"], fg=t["title"])
        self.transcript_chip.config(bg=t["panel"], fg=t["chip_fg"])
        self.transcript_canvas.config(bg=t["panel"])
        self.transcript_content.config(bg=t["panel"])
        self._apply_conversation_theme()

        # Session panel
        self.control_header.config(bg=t["panel"])
        self.control_title.config(bg=t["panel"], fg=t["title"])
        self.control_chip.config(bg=t["panel"], fg=t["chip_fg"])
        for row in self.summary_rows:
            row["frame"].config(bg=t["panel"])
            row["title"].config(bg=t["panel"], fg=t["muted"])
            row["copy"].config(bg=t["panel"], fg=t["text"])
            if row["sep_after"]:
                row["sep_after"].config(bg=t["border"])
        if self.footer_note:
            self.footer_note.config(bg=t["panel"], fg=t["muted"])

        self._configure_notebook_style()
        self._draw_mic_meter()
        self._draw_pulse_dots()
        self._refresh_dynamic_copy()

    # ------------------------------------------------------------------
    # Notebook style (Settings window)
    # ------------------------------------------------------------------
    def _configure_notebook_style(self):
        t = self.theme
        self.ttk_style.configure(
            "Locus.TNotebook",
            background=t["panel"],
            borderwidth=0,
            tabmargins=(0, 0, 0, 0),
        )
        self.ttk_style.configure(
            "Locus.TNotebook.Tab",
            background=t["shell"],
            foreground=t["muted"],
            padding=(18, 10),
            borderwidth=0,
            font=("Segoe UI", 9, "bold"),
        )
        self.ttk_style.map(
            "Locus.TNotebook.Tab",
            background=[("selected", t["chip_bg"]), ("active", t["panel_alt"])],
            foreground=[("selected", t["chip_fg"]), ("active", t["text"])],
        )

    # ------------------------------------------------------------------
    # Dynamic copy refresh
    # ------------------------------------------------------------------
    def _refresh_dynamic_copy(self):
        if self.summary_rows:
            self.summary_rows[0]["copy"].config(text=config.MODEL_NAME)
            self.summary_rows[1]["copy"].config(text=", ".join(config.WAKE_WORDS))
            self.summary_rows[3]["copy"].config(text=self._build_audio_summary())
        self.hero_caption.config(text="Wake words: " + ", ".join(config.WAKE_WORDS))
        self._update_quick_stats()

    def _build_audio_summary(self):
        input_label  = config.MICROPHONE_DEVICE_ID or "system default"
        output_label = getattr(config, "OUTPUT_AUDIO_DEVICE_ID", "") or "system default"
        return f"Input: {input_label}\nOutput: {output_label}"

    def _update_quick_stats(self):
        gemini_ready = "Gemini Ready" if str(config.GOOGLE_API_KEY or "").strip() else "Gemini Disabled"
        labels = ["Wake Word Ready", "Manual Trigger Enabled", gemini_ready]
        for stat, label_text in zip(self.quick_stats, labels):
            stat["label"].config(text=label_text)

    # ------------------------------------------------------------------
    # Conversation helpers
    # ------------------------------------------------------------------
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
        card.pack(fill="x", pady=(0, 8))

        role_text  = "YOU" if role == "user" else "LOCUS"
        role_label = tk.Label(
            card,
            text=role_text,
            font=("Segoe UI", 8, "bold"),
            anchor="w",
        )
        role_label.pack(fill="x", padx=14, pady=(10, 3))

        text_label = tk.Label(
            card,
            text=normalized,
            font=("Segoe UI", 11),
            justify="left",
            anchor="w",
            wraplength=520,
        )
        text_label.pack(fill="x", padx=14, pady=(0, 10))

        message = {
            "role":       role,
            "frame":      card,
            "role_label": role_label,
            "text_label": text_label,
        }
        self.message_widgets.append(message)
        self.conversation_messages.append({"role": role, "text": normalized})
        self._apply_conversation_theme()
        self._scroll_conversation_to_bottom()
        return text_label

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
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
            self.summary_rows[2]["copy"].config(text=detail or text)
        self.voice_intro.config(text=detail or text)
        if detail is not None:
            self.status_subtext.config(text=detail)

    def set_transcript(self, user_text=None, locus_text=None):
        if user_text is not None:
            self.user_text_label  = self._append_conversation_message("user",  user_text)
        if locus_text is not None:
            self.locus_text_label = self._append_conversation_message("locus", locus_text)

    def set_mic_state(self, state, detail=None):
        self.mic_state = state
        labels = {
            "idle":      "Idle",
            "listening": "Listening",
            "thinking":  "Thinking",
            "error":     "Error",
        }
        label     = labels.get(state, "Idle")
        color_key = STATUS_TONES.get(state, "muted")

        self.mic_mode_label.config(text=label, fg=self.theme["chip_fg"])
        self.top_status_chip.config(text=label, fg=self.theme["status_badge_fg"])
        self.voice_meta_state.config(
            text=(
                "Live"       if state == "listening" else
                "Processing" if state == "thinking"  else
                "Passive"    if state == "idle"       else "Error"
            ),
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

    # ------------------------------------------------------------------
    # Bar loop & waveform drawing
    # ------------------------------------------------------------------
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

        width  = max(canvas.winfo_width(),  280)
        height = max(canvas.winfo_height(), 72)
        count  = 28
        gap    = 3
        start_x = 10
        usable_width = width - (start_x * 2)
        bar_width = max(4, int((usable_width - (gap * (count - 1))) / count))
        baseline  = height - 8

        for index in range(count):
            x1 = start_x + index * (bar_width + gap)
            x2 = x1 + bar_width

            if self.mic_state == "listening":
                raw  = 10 + int(self.smoothed_level * 40) + abs(((self.bar_tick + index) % 8) - 4) * 3
                fill = self.theme["bar_on"] if index % 3 != 0 else self.theme["accent"]
            elif self.mic_state == "thinking":
                raw  = 8 + abs(((self.bar_tick + index) % 10) - 5) * 4
                fill = self.theme["accent_alt"] if index % 4 == 0 else self.theme["bar_off"]
            elif self.mic_state == "error":
                raw  = 6 + (2 if index < 4 else 0)
                fill = self.theme["danger"] if index < 5 else self.theme["bar_off"]
            else:
                raw  = 4 + abs(((index) % 8) - 4) + (index % 5)
                fill = self.theme["bar_off"]

            bar_height = min(52, raw)
            y1 = baseline - bar_height
            y2 = baseline
            canvas.create_rectangle(x1, y1, x2, y2, fill=fill, outline="")

        self._draw_voice_history_strip()

    def _draw_voice_history_strip(self):
        import math
        canvas = self.history_canvas
        canvas.delete("all")

        width  = max(canvas.winfo_width(),  220)
        height = max(canvas.winfo_height(), 36)
        count  = 20
        gap    = 4
        start_x = 8
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

    # ------------------------------------------------------------------
    # Cat image fade animation
    # ------------------------------------------------------------------
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

        steps    = 8
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

    # ------------------------------------------------------------------
    # Resize handler
    # ------------------------------------------------------------------
    def _handle_resize(self, event):
        if event.widget is not self.root:
            return
        transcript_width = max(260, self.transcript_card.winfo_width() - 80)
        for message in self.message_widgets:
            message["text_label"].config(wraplength=transcript_width)
        control_width = max(220, self.control_card.winfo_width() - 80)
        for row in self.summary_rows:
            row["copy"].config(wraplength=control_width)
        self._draw_mic_meter()

    # ------------------------------------------------------------------
    # Settings window
    # ------------------------------------------------------------------
    def open_settings_window(self):
        if self.settings_window and self.settings_window.winfo_exists():
            self.settings_window.focus_force()
            return

        settings_service = get_settings_service()
        current_settings = load_settings()
        input_devices  = [{"id": "", "label": "System default input"}]  + settings_service.list_input_audio_devices()
        output_devices = [{"id": "", "label": "System default output"}] + settings_service.list_output_audio_devices()
        self._append_stale_device(input_devices,  current_settings["microphone_device_id"],    "Unavailable saved input")
        self._append_stale_device(output_devices, current_settings["output_audio_device_id"],  "Unavailable saved output")

        error_labels = {}
        window = tk.Toplevel(self.root)
        self.settings_window = window
        window.title("Settings")
        window.geometry("760x860")
        window.minsize(760, 860)
        window.transient(self.root)
        window.grab_set()
        window.config(bg=self.theme["root_bg"])

        shell = tk.Frame(
            window,
            bg=self.theme["shell"],
            highlightthickness=1,
            highlightbackground=self.theme["shell_border"],
        )
        shell.pack(fill="both", expand=True, padx=20, pady=20)

        # Sidebar
        settings_sidebar = tk.Frame(shell, bg=self.theme["sidebar"], width=96, highlightthickness=0)
        settings_sidebar.pack(side="left", fill="y")
        settings_sidebar.pack_propagate(False)

        settings_sidebar_inner = tk.Frame(settings_sidebar, bg=self.theme["sidebar"])
        settings_sidebar_inner.pack(fill="both", expand=True, padx=14, pady=18)

        settings_brand = tk.Frame(
            settings_sidebar_inner,
            bg=self.theme["accent"],
            width=4, height=108,
        )
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

        heading = tk.Label(
            header_copy,
            text="Settings",
            font=("Segoe UI Semibold", 26),
            bg=self.theme["shell"],
            fg=self.theme["title"],
        )
        heading.pack(anchor="w")

        subheading = tk.Label(
            header_copy,
            text="General and voice settings are saved locally. Gemini API access is read from .env.",
            font=("Segoe UI", 10),
            bg=self.theme["shell"],
            fg=self.theme["muted"],
        )
        subheading.pack(anchor="w", pady=(4, 0))

        settings_chip = tk.Label(
            header,
            text="Local Config",
            font=("Segoe UI", 9, "bold"),
            padx=12, pady=8,
            bg=self.theme["status_badge_bg"],
            fg=self.theme["status_badge_fg"],
        )
        settings_chip.pack(side="right", anchor="n")

        notebook_shell = tk.Frame(
            shell_main,
            bg=self.theme["panel"],
            highlightthickness=1,
            highlightbackground=self.theme["border"],
        )
        notebook_shell.pack(fill="both", expand=True, padx=24, pady=(0, 18))

        notebook = ttk.Notebook(notebook_shell, style="Locus.TNotebook")
        notebook.pack(fill="both", expand=True, padx=18, pady=18)

        general_tab,    general_content    = self._build_scrollable_settings_tab(notebook)
        voice_tab,      voice_content      = self._build_scrollable_settings_tab(notebook)
        appearance_tab, appearance_content = self._build_scrollable_settings_tab(notebook)
        notebook.add(general_tab,    text="General")
        notebook.add(voice_tab,      text="Voice")
        notebook.add(appearance_tab, text="Appearance")

        api_key_var = tk.StringVar(value=load_gemini_api_key())
        model_var   = tk.StringVar(value=current_settings["gemini_model"])
        language_choice_var = tk.StringVar(
            value=current_settings["language_code"] if current_settings["language_code"] in LANGUAGE_OPTIONS else "custom"
        )
        custom_language_var = tk.StringVar(
            value="" if current_settings["language_code"] in LANGUAGE_OPTIONS else current_settings["language_code"]
        )
        wake_word_vars = {
            key: tk.BooleanVar(value=key in current_settings["wake_words"])
            for key in WAKE_WORD_PRESET_OPTIONS
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
            value=self._get_audio_device_label(current_settings["output_audio_device_id"], output_devices, "System default output")
        )
        theme_var          = tk.StringVar(value=current_settings["theme"])
        animation_speed_var = tk.StringVar(value=current_settings["animation_speed"])

        error_labels["gemini_api_key"], gemini_status_label = self._build_setting_field(
            general_content, "Gemini API key", api_key_var,
            "Saved to .env as GEMINI_KEY and masked in this window.",
            show="*", include_status=True,
        )
        error_labels["gemini_model"] = self._build_setting_field(
            general_content, "Gemini model", model_var,
            "Example: gemini-flash-latest",
        )
        error_labels["language_code"] = self._build_language_selector(
            voice_content, language_choice_var, custom_language_var,
        )
        error_labels["wake_words"] = self._build_wake_word_selector(
            voice_content, wake_word_vars, custom_wake_words_var,
        )
        error_labels["microphone_device_id"] = self._build_microphone_selector(
            voice_content, "Input audio device", input_device_var, input_devices,
            "Select the microphone/input device or keep the system default.",
        )
        error_labels["output_audio_device_id"] = self._build_microphone_selector(
            voice_content, "Output audio device", output_device_var, output_devices,
            "Saved for future playback routing. Current app playback does not use this yet.",
        )
        error_labels["theme"]           = self._build_theme_selector(appearance_content, theme_var)
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
            effective_wake_words    = self._resolve_wake_words(wake_word_vars, custom_wake_words_var.get())
            validation = validate_settings_input({
                "gemini_model":          model_var.get(),
                "language_code":         effective_language_code,
                "wake_words":            effective_wake_words,
                "microphone_device_id":  self._get_audio_device_id(input_device_var.get(),  input_devices),
                "output_audio_device_id": self._get_audio_device_id(output_device_var.get(), output_devices),
                "theme":                 theme_var.get(),
                "animation_speed":       animation_speed_var.get(),
            })
            if not validation.is_valid:
                gemini_status_label.config(text="")
                for field_name, message in validation.errors.items():
                    label = error_labels.get(field_name)
                    if label:
                        label.config(text=message)
                return

            normalized_api_key = api_key_var.get().strip()
            gemini_validation  = None
            if normalized_api_key:
                gemini_status_label.config(text="Checking Gemini access...", fg=self.theme["muted"])
                window.update_idletasks()
                gemini_validation = validate_gemini_configuration(normalized_api_key, model_var.get())
            else:
                gemini_status_label.config(
                    text="Gemini key is empty. Gemini features will stay disabled.",
                    fg=self.theme["warning"],
                )

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
                    gemini_status_label.config(
                        text="Settings saved, but Gemini could not be verified.",
                        fg=self.theme["warning"],
                    )
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
            button_row, text="Cancel",
            font=("Segoe UI", 10, "bold"), relief="flat",
            bg=self.theme["secondary_bg"], fg=self.theme["secondary_fg"],
            command=close_window, cursor="hand2", padx=18, pady=10,
        )
        cancel_btn.pack(side="right", padx=(10, 0))

        save_btn = tk.Button(
            button_row, text="Save",
            font=("Segoe UI", 10, "bold"), relief="flat",
            bg=self.theme["button_bg"], fg=self.theme["button_fg"],
            command=save_and_apply, cursor="hand2", padx=18, pady=10,
        )
        save_btn.pack(side="right")

        window.protocol("WM_DELETE_WINDOW", close_window)

    # ------------------------------------------------------------------
    # Settings sub-builders
    # ------------------------------------------------------------------
    def _build_scrollable_settings_tab(self, notebook):
        tab    = tk.Frame(notebook, bg=self.theme["panel"])
        canvas = tk.Canvas(tab, bg=self.theme["panel"], highlightthickness=0, bd=0, relief="flat")
        scrollbar = ttk.Scrollbar(tab, orient="vertical", command=canvas.yview)
        content   = tk.Frame(canvas, bg=self.theme["panel"])

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
        canvas.bind("<Enter>", lambda _e: canvas.bind_all("<MouseWheel>", on_mousewheel))
        canvas.bind("<Leave>", lambda _e: canvas.unbind_all("<MouseWheel>"))

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        return tab, content

    def _build_setting_field(self, parent, label_text, variable, note, show=None, include_status=False):
        block = tk.Frame(
            parent, bg=self.theme["panel_alt"],
            highlightthickness=1, highlightbackground=self.theme["border"],
        )
        block.pack(fill="x", padx=18, pady=(18, 0))

        label = tk.Label(block, text=label_text, font=("Segoe UI", 10, "bold"),
                         bg=self.theme["panel_alt"], fg=self.theme["title"])
        label.pack(anchor="w", padx=16, pady=(16, 6))

        entry = tk.Entry(
            block, textvariable=variable, relief="flat", font=("Segoe UI", 10),
            bg=self.theme["input_bg"], fg=self.theme["input_fg"],
            insertbackground=self.theme["input_fg"], show=show,
        )
        entry.pack(fill="x", padx=16, pady=(0, 10), ipady=10)

        note_label = tk.Label(block, text=note, font=("Segoe UI", 8),
                              bg=self.theme["panel_alt"], fg=self.theme["muted"])
        note_label.pack(anchor="w", padx=16, pady=(0, 4))

        status_label = None
        if include_status:
            status_label = tk.Label(block, text="", font=("Segoe UI", 8, "bold"),
                                    bg=self.theme["panel_alt"], fg=self.theme["success"])
            status_label.pack(anchor="w", padx=16, pady=(0, 4))

        error_label = tk.Label(block, text="", font=("Segoe UI", 8, "bold"),
                               bg=self.theme["panel_alt"], fg=self.theme["danger"])
        error_label.pack(anchor="w", padx=16, pady=(0, 16))

        if include_status:
            return error_label, status_label
        return error_label

    def _build_language_selector(self, parent, selection_var, custom_var):
        block = tk.Frame(
            parent, bg=self.theme["panel_alt"],
            highlightthickness=1, highlightbackground=self.theme["border"],
        )
        block.pack(fill="x", padx=18, pady=(18, 0))

        label = tk.Label(block, text="Language", font=("Segoe UI", 10, "bold"),
                         bg=self.theme["panel_alt"], fg=self.theme["title"])
        label.pack(anchor="w", padx=16, pady=(16, 6))

        values = [meta["label"] for meta in LANGUAGE_OPTIONS.values()] + ["Custom code"]
        display_by_value = {code: meta["label"] for code, meta in LANGUAGE_OPTIONS.items()}
        display_by_value["custom"] = "Custom code"
        value_by_display = {d: v for v, d in display_by_value.items()}
        selection_display = tk.StringVar(value=display_by_value.get(selection_var.get(), "Custom code"))

        def sync_language_choice(*_):
            selection_var.set(value_by_display.get(selection_display.get(), "custom"))
            custom_entry.config(state="normal" if selection_var.get() == "custom" else "disabled")

        combo = ttk.Combobox(block, textvariable=selection_display, values=values,
                             state="readonly", font=("Segoe UI", 10))
        combo.pack(fill="x", padx=16, pady=(0, 10), ipady=7)
        selection_display.trace_add("write", sync_language_choice)

        custom_entry = tk.Entry(
            block, textvariable=custom_var, relief="flat", font=("Segoe UI", 10),
            bg=self.theme["input_bg"], fg=self.theme["input_fg"],
            insertbackground=self.theme["input_fg"],
        )
        custom_entry.pack(fill="x", padx=16, pady=(0, 10), ipady=10)
        sync_language_choice()

        note_label = tk.Label(
            block, text="Pick a common language or enter a custom recognition code like en-US.",
            font=("Segoe UI", 8), bg=self.theme["panel_alt"], fg=self.theme["muted"],
        )
        note_label.pack(anchor="w", padx=16, pady=(0, 4))

        error_label = tk.Label(block, text="", font=("Segoe UI", 8, "bold"),
                               bg=self.theme["panel_alt"], fg=self.theme["danger"])
        error_label.pack(anchor="w", padx=16, pady=(0, 16))
        return error_label

    def _build_wake_word_selector(self, parent, wake_word_vars, custom_var):
        block = tk.Frame(
            parent, bg=self.theme["panel_alt"],
            highlightthickness=1, highlightbackground=self.theme["border"],
        )
        block.pack(fill="x", padx=18, pady=(18, 0))

        label = tk.Label(block, text="Wake words", font=("Segoe UI", 10, "bold"),
                         bg=self.theme["panel_alt"], fg=self.theme["title"])
        label.pack(anchor="w", padx=16, pady=(16, 10))

        for key, metadata in WAKE_WORD_PRESET_OPTIONS.items():
            check = tk.Checkbutton(
                block, text=metadata["label"], variable=wake_word_vars[key],
                onvalue=True, offvalue=False,
                bg=self.theme["panel_alt"], fg=self.theme["text"],
                activebackground=self.theme["panel_alt"], activeforeground=self.theme["title"],
                selectcolor=self.theme["panel"], font=("Segoe UI", 10), anchor="w",
            )
            check.pack(anchor="w", padx=16, pady=(0, 4))

        custom_label = tk.Label(block, text="Custom wake words", font=("Segoe UI", 9, "bold"),
                                bg=self.theme["panel_alt"], fg=self.theme["title"])
        custom_label.pack(anchor="w", padx=16, pady=(12, 4))

        custom_entry = tk.Entry(
            block, textvariable=custom_var, relief="flat", font=("Segoe UI", 10),
            bg=self.theme["input_bg"], fg=self.theme["input_fg"],
            insertbackground=self.theme["input_fg"],
        )
        custom_entry.pack(fill="x", padx=16, pady=(0, 10), ipady=10)

        note_label = tk.Label(
            block, text="Choose built-in wake words and optionally add your own words, separated by commas.",
            font=("Segoe UI", 8), bg=self.theme["panel_alt"], fg=self.theme["muted"],
        )
        note_label.pack(anchor="w", padx=16, pady=(0, 4))

        error_label = tk.Label(block, text="", font=("Segoe UI", 8, "bold"),
                               bg=self.theme["panel_alt"], fg=self.theme["danger"])
        error_label.pack(anchor="w", padx=16, pady=(0, 16))
        return error_label

    def _build_microphone_selector(self, parent, label_text, variable, devices, note):
        block = tk.Frame(
            parent, bg=self.theme["panel_alt"],
            highlightthickness=1, highlightbackground=self.theme["border"],
        )
        block.pack(fill="x", padx=18, pady=(18, 0))

        label = tk.Label(block, text=label_text, font=("Segoe UI", 10, "bold"),
                         bg=self.theme["panel_alt"], fg=self.theme["title"])
        label.pack(anchor="w", padx=16, pady=(16, 6))

        values = [device["label"] for device in devices]
        combo  = ttk.Combobox(block, textvariable=variable, values=values,
                              state="readonly", font=("Segoe UI", 10))
        combo.pack(fill="x", padx=16, pady=(0, 10), ipady=7)

        note_label = tk.Label(block, text=note, font=("Segoe UI", 8),
                              bg=self.theme["panel_alt"], fg=self.theme["muted"])
        note_label.pack(anchor="w", padx=16, pady=(0, 4))

        error_label = tk.Label(block, text="", font=("Segoe UI", 8, "bold"),
                               bg=self.theme["panel_alt"], fg=self.theme["danger"])
        error_label.pack(anchor="w", padx=16, pady=(0, 16))
        return error_label

    def _build_theme_selector(self, parent, variable):
        block = tk.Frame(
            parent, bg=self.theme["panel_alt"],
            highlightthickness=1, highlightbackground=self.theme["border"],
        )
        block.pack(fill="x", padx=14, pady=(14, 0))

        label = tk.Label(block, text="UI style", font=("Segoe UI", 10, "bold"),
                         bg=self.theme["panel_alt"], fg=self.theme["title"])
        label.pack(anchor="w", padx=14, pady=(14, 10))

        for key, metadata in THEME_OPTIONS.items():
            row = tk.Frame(block, bg=self.theme["panel_alt"])
            row.pack(fill="x", padx=14, pady=(0, 10))

            radio = tk.Radiobutton(
                row, text=metadata["label"], value=key, variable=variable,
                bg=self.theme["panel_alt"], fg=self.theme["text"],
                selectcolor=self.theme["panel"],
                activebackground=self.theme["panel_alt"], activeforeground=self.theme["title"],
                font=("Segoe UI", 10, "bold"), anchor="w",
            )
            radio.pack(anchor="w")

            desc = tk.Label(
                row, text=metadata["description"], font=("Segoe UI", 8),
                bg=self.theme["panel_alt"], fg=self.theme["muted"],
            )
            desc.pack(anchor="w", padx=(24, 0))

        error_label = tk.Label(block, text="", font=("Segoe UI", 8, "bold"),
                               bg=self.theme["panel_alt"], fg=self.theme["danger"])
        error_label.pack(anchor="w", padx=14, pady=(0, 14))
        return error_label

    def _build_speed_selector(self, parent, variable):
        block = tk.Frame(
            parent, bg=self.theme["panel_alt"],
            highlightthickness=1, highlightbackground=self.theme["border"],
        )
        block.pack(fill="x", padx=14, pady=(14, 0))

        label = tk.Label(block, text="Animation speed", font=("Segoe UI", 10, "bold"),
                         bg=self.theme["panel_alt"], fg=self.theme["title"])
        label.pack(anchor="w", padx=14, pady=(14, 10))

        options = tk.Frame(block, bg=self.theme["panel_alt"])
        options.pack(fill="x", padx=14, pady=(0, 14))

        for key, metadata in ANIMATION_SPEED_OPTIONS.items():
            radio = tk.Radiobutton(
                options, text=metadata["label"], value=key, variable=variable,
                bg=self.theme["panel_alt"], fg=self.theme["text"],
                selectcolor=self.theme["panel"],
                activebackground=self.theme["panel_alt"], activeforeground=self.theme["title"],
                font=("Segoe UI", 10),
            )
            radio.pack(side="left", padx=(0, 18))

        error_label = tk.Label(block, text="", font=("Segoe UI", 8, "bold"),
                               bg=self.theme["panel_alt"], fg=self.theme["danger"])
        error_label.pack(anchor="w", padx=14, pady=(0, 14))
        return error_label

    # ------------------------------------------------------------------
    # Helper utilities
    # ------------------------------------------------------------------
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
        selected_words = [key for key, var in wake_word_vars.items() if var.get()]
        custom_words   = [w for w in custom_wake_words.split(",")] if custom_wake_words else []
        return selected_words + custom_words
