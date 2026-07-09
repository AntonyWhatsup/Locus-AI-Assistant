import tkinter as tk
import threading
from src.ui_manager import LocusUI
from src.processor import background_listener, reload_model, manual_activation
from src.brain.trainer_module import run_training
from src.actions import reload_gemini_client
from src.settings_manager import apply_settings, load_settings

def start_sequence(ui):
    ui.root.after(0, lambda: ui.fade_to_image("train"))
    ui.root.after(0, lambda: ui.set_status("Updating brain...", "thinking", "Training the local intent model."))
    ui.root.after(0, lambda: ui.set_mic_state("thinking", "Training the local intent model."))

    def task():
        try:
            run_training()
            reload_model()
        except Exception as e:
            print(f"Training Failed: {e}")

        ui.root.after(0, lambda: ui.fade_to_image("idle"))
        ui.root.after(0, lambda: ui.set_mic_state("idle", "Ready for the next wake word."))
        ui.root.after(0, lambda: ui.set_status("Say 'Locus'", "idle", "Left-click the cat or wait for the wake word."))

        threading.Thread(target=background_listener, args=(ui,), daemon=True).start()

    threading.Thread(target=task, daemon=True).start()

if __name__ == "__main__":
    apply_settings(load_settings())
    reload_gemini_client()

    root = tk.Tk()
    ui = LocusUI(root)
    ui.set_manual_action(lambda: manual_activation(ui))
    ui.image_label.bind("<Button-1>", lambda e: manual_activation(ui))

    start_sequence(ui)

    root.mainloop()
