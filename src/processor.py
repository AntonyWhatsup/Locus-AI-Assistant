import speech_recognition as sr
import threading
import torch
import time
from src.config import LANG_CODE, WAKE_WORDS, MODEL_DATA_PATH
from src.brain.model import NeuralNet
from src.brain.nltk_utils import bag_of_words, tokenize
from src.actions import ask_gemini, execute_command_logic

# Global variables
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model, all_words, tags = None, None, None
is_processing = False
active_context = None

def reload_model():
    """Loads new brain (model) after training is complete."""
    global model, all_words, tags
    try:
        data = torch.load(MODEL_DATA_PATH, map_location=device)
        model = NeuralNet(data["input_size"], data["hidden_size"], data["output_size"]).to(device)
        model.load_state_dict(data["model_state"])
        model.eval()
        all_words, tags = data["all_words"], data["tags"]
        print(f"LOG: Brain reloaded (Continuous Mode).")
    except Exception as e:
        print(f"Reload Error: {e}")

def manual_activation(ui):
    """Manually activate listening after clicking the cat."""
    if not is_processing:
        print("LOG: Manual activation via click.")
        threading.Thread(target=listen_and_process, args=(ui,)).start()

def listen_and_process(ui):
    global is_processing, active_context
    is_processing = True
    r = sr.Recognizer()
    r.pause_threshold = 1.0 

    while True:
        # UI update based on context
        if active_context:
            ui.root.after(0, lambda: ui.status_label.config(text="WHICH PROFILE?", fg="orange"))
            ui.root.after(0, lambda: ui.fade_to_image("think")) 
        else:
            ui.root.after(0, lambda: ui.status_label.config(text="Listening...", fg="red"))
            ui.root.after(0, lambda: ui.fade_to_image("listen"))

        ui.root.after(0, ui.start_visualizer)

        with sr.Microphone() as source:
            try:
                # Listening
                audio = r.listen(source, timeout=5, phrase_time_limit=7)
                ui.root.after(0, ui.stop_visualizer)
                
                ui.root.after(0, lambda: ui.status_label.config(text="Thinking...", fg="blue"))
                ui.root.after(0, lambda: ui.fade_to_image("think"))

                text = r.recognize_google(audio, language=LANG_CODE)
                ui.root.after(0, lambda: ui.user_speech_label.config(text=f"You: {text}"))

                # Processing
                X = torch.from_numpy(bag_of_words(tokenize(text), all_words).reshape(1, -1)).to(device)
                output = model(X)
                prob, predicted = torch.max(torch.softmax(output, dim=1), dim=1)
                tag = tags[predicted.item()]
                conf = prob.item()

                print(f"LOG: Heard '{text}' -> {tag} ({conf:.2f})")

                # Logic
                res, active_context = execute_command_logic(tag, conf, active_context)
                
                # --- UI Feedback ---
                if res == "ask_profile_yt":
                    ui.root.after(0, lambda: ui.status_label.config(text="WHICH YOUTUBE PROFILE?", fg="orange"))
                    ui.root.after(0, lambda: ui.user_speech_label.config(text="Locus: Anton, Clean or Default?"))
                    time.sleep(0.5)

                elif res == "ask_profile_chrome":
                    ui.root.after(0, lambda: ui.status_label.config(text="WHICH CHROME PROFILE?", fg="orange"))
                    ui.root.after(0, lambda: ui.user_speech_label.config(text="Locus: Please choose account..."))
                    time.sleep(0.5)

                elif res == "gemini_cool_request":
                    ui.root.after(0, lambda: ui.fade_to_image("cool"))
                    ans = ask_gemini(f"Answer cool/short: {text}")
                    ui.root.after(0, lambda: ui.user_speech_label.config(text=f"Locus: {ans}"))
                    time.sleep(3)

                elif res == "gemini_request":
                    ui.root.after(0, lambda: ui.fade_to_image("speak"))
                    ans = ask_gemini(text)
                    ui.root.after(0, lambda: ui.user_speech_label.config(text=f"Locus: {ans}"))
                    time.sleep(3)

                elif res == "success":
                    ui.root.after(0, lambda: ui.fade_to_image("success"))
                    ui.root.after(0, lambda: ui.status_label.config(text="Success!", fg="green"))
                    time.sleep(1)

                elif res == "bye":
                    ui.root.after(0, lambda: ui.fade_to_image("success"))
                    ui.root.after(0, ui.root.quit)
                    return

            except sr.WaitTimeoutError:
                print("LOG: Timeout. Sleeping.")
                break 
            except sr.UnknownValueError:
                ui.root.after(0, lambda: ui.status_label.config(text="Come again?", fg="orange"))
                time.sleep(1)
                continue
            except Exception as e:
                print(f"Error: {e}")
                break

    is_processing = False
    ui.root.after(0, ui.stop_visualizer)
    ui.root.after(0, lambda: ui.fade_to_image("idle"))
    ui.root.after(0, lambda: ui.status_label.config(text="Say 'Locus'", fg="black"))

def background_listener(ui):
    r = sr.Recognizer()
    while True:
        if not is_processing:
            with sr.Microphone() as source:
                try:
                    audio = r.listen(source, phrase_time_limit=3)
                    text = r.recognize_google(audio, language=LANG_CODE).lower()
                    if any(w in text for w in WAKE_WORDS):
                        threading.Thread(target=listen_and_process, args=(ui,)).start()
                except: pass
        time.sleep(0.1)
