import tkinter as tk
import threading
from src.ui_manager import LocusUI
from src.processor import background_listener, reload_model, manual_activation
from src.brain.trainer_module import run_training

def start_sequence(ui):
    # 1. Obraz treningowy
    ui.root.after(0, lambda: ui.fade_to_image("train"))
    ui.root.after(0, lambda: ui.status_label.config(text="Updating Brain...", fg="purple"))
    
    def task():
        # 2. Trening
        try:
            run_training() 
            reload_model()
        except Exception as e:
            print(f"Training Failed: {e}")
        
        # 3. Tryb normalny
        ui.root.after(0, lambda: ui.fade_to_image("idle"))
        ui.root.after(0, lambda: ui.status_label.config(text="Say 'Locus'", fg="black"))
        
        # 4. Tło
        threading.Thread(target=background_listener, args=(ui,), daemon=True).start()

    threading.Thread(target=task, daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    ui = LocusUI(root)
    
    # --- NOWOŚĆ: Obsługa kliknięcia (Click-to-Listen) ---
    # Kliknięcie lewym przyciskiem myszy (<Button-1>) aktywuje nasłuchiwanie
    ui.image_label.bind("<Button-1>", lambda e: manual_activation(ui))
    
    start_sequence(ui)
    
    root.mainloop()