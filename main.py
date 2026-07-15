import tkinter as tk
import threading
from src.ui_manager import LocusUI
from src.processor import background_listener, reload_model, manual_activation
from src.brain.trainer_module import run_training
from src.actions import reload_gemini_client
from src.settings_manager import apply_settings, load_settings

def start_sequence(ui):
    ui.root.after(0, lambda: ui.fade_to_image("train"))
    ui.root.after(0, lambda: ui.set_status("Preparing brain...", "thinking", "Checking whether the local intent model needs retraining."))
    ui.root.after(0, lambda: ui.set_mic_state("thinking", "Checking whether the local intent model needs retraining."))

    def task():
        try:
            trained = run_training()
            reload_ok = reload_model()
            if not reload_ok:
                ui.root.after(0, lambda: ui.set_status("Brain load failed", "error", "The local model could not be loaded."))
                ui.root.after(0, lambda: ui.set_transcript(locus_text="The local intent model failed to load. Check the console for details."))
                return

            if trained:
                ui.root.after(0, lambda: ui.set_status("Brain updated", "success", "The local intent model was retrained successfully."))
            else:
                ui.root.after(0, lambda: ui.set_status("Brain ready", "success", "The cached local intent model is already up to date."))
        except Exception as exc:
            print(f"Training Failed: {exc}")
            ui.root.after(0, lambda: ui.set_status("Startup failed", "error", "The local model could not be prepared."))
            ui.root.after(0, lambda: ui.set_transcript(locus_text="Startup failed while preparing the local model."))
            return

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
