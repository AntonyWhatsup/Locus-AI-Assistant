import audioop
import threading
import time

import speech_recognition as sr
import torch

import src.config as config
from src.actions import ask_gemini, execute_command_logic
from src.brain.model import NeuralNet
from src.brain.nltk_utils import bag_of_words, tokenize


device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model, all_words, tags = None, None, None
is_processing = False
active_context = None


def reload_model():
    """Load the trained model from disk."""
    global model, all_words, tags
    try:
        data = torch.load(config.MODEL_DATA_PATH, map_location=device)
        model = NeuralNet(data["input_size"], data["hidden_size"], data["output_size"]).to(device)
        model.load_state_dict(data["model_state"])
        model.eval()
        all_words, tags = data["all_words"], data["tags"]
        print("LOG: Brain reloaded (Continuous Mode).")
    except Exception as exc:
        print(f"Reload Error: {exc}")


def manual_activation(ui):
    """Manually trigger listening."""
    if not is_processing:
        print("LOG: Manual activation via click.")
        threading.Thread(target=listen_and_process, args=(ui,), daemon=True).start()


def _normalize_level(frame_data, sample_width):
    try:
        rms = audioop.rms(frame_data, sample_width)
    except audioop.error:
        return 0.0
    return min(1.0, rms / 2500.0)


def _capture_phrase(recognizer, source, ui):
    chunks = []
    stream = recognizer.listen(source, timeout=5, phrase_time_limit=7, stream=True)
    for chunk in stream:
        chunks.append(chunk.frame_data)
        level = _normalize_level(chunk.frame_data, chunk.sample_width)
        ui.root.after(0, lambda lvl=level: ui.update_mic_level(lvl))

    if not chunks:
        raise sr.UnknownValueError()

    return sr.AudioData(b"".join(chunks), source.SAMPLE_RATE, source.SAMPLE_WIDTH)


def _classify_text(text):
    X = torch.from_numpy(bag_of_words(tokenize(text), all_words).reshape(1, -1)).to(device)
    output = model(X)
    prob, predicted = torch.max(torch.softmax(output, dim=1), dim=1)
    tag = tags[predicted.item()]
    return tag, prob.item()


def listen_and_process(ui):
    global is_processing, active_context
    if model is None or all_words is None or tags is None:
        ui.root.after(0, lambda: ui.set_status("Brain not ready", "prompt", "Wait until training finishes, then try again."))
        ui.root.after(0, lambda: ui.set_transcript(locus_text="The local model is still loading."))
        return

    is_processing = True
    recognizer = sr.Recognizer()
    recognizer.pause_threshold = 1.0

    while True:
        if active_context:
            ui.root.after(0, lambda: ui.set_status("Which profile?", "prompt", "Choose a Chrome profile to continue."))
            ui.root.after(0, lambda: ui.fade_to_image("think"))
            ui.root.after(0, lambda: ui.set_mic_state("listening", "Waiting for your profile answer..."))
        else:
            ui.root.after(0, lambda: ui.set_status("Listening...", "listening", "Speak after the cat changes state."))
            ui.root.after(0, lambda: ui.fade_to_image("listen"))

        if active_context:
            ui.root.after(0, lambda: ui.start_visualizer("Waiting for your profile answer..."))
        else:
            ui.root.after(0, ui.start_visualizer)

        try:
            with sr.Microphone() as source:
                audio = _capture_phrase(recognizer, source, ui)
                ui.root.after(0, ui.stop_visualizer)

                ui.root.after(0, lambda: ui.set_status("Thinking...", "thinking", "Processing your request..."))
                ui.root.after(0, lambda: ui.set_mic_state("thinking", "Processing your request..."))
                ui.root.after(0, lambda: ui.fade_to_image("think"))

                text = recognizer.recognize_google(audio, language=config.LANG_CODE)
                ui.root.after(0, lambda captured=text: ui.set_transcript(user_text=captured))

                tag, conf = _classify_text(text)
                print(f"LOG: Heard '{text}' -> {tag} ({conf:.2f})")

                res, active_context = execute_command_logic(tag, conf, active_context)

                if res == "ask_profile_yt":
                    ui.root.after(0, lambda: ui.set_status("Which YouTube profile?", "prompt", "Answer with Anton, Clean, or Default."))
                    ui.root.after(0, lambda: ui.set_transcript(locus_text="Anton, Clean, or Default?"))
                    time.sleep(0.5)

                elif res == "ask_profile_chrome":
                    ui.root.after(0, lambda: ui.set_status("Which Chrome profile?", "prompt", "Answer with Anton, Clean, or Default."))
                    ui.root.after(0, lambda: ui.set_transcript(locus_text="Please choose an account."))
                    time.sleep(0.5)

                elif res == "gemini_cool_request":
                    ui.root.after(0, lambda: ui.fade_to_image("cool"))
                    ans = ask_gemini(f"Answer cool and short: {text}")
                    ui.root.after(0, lambda answer=ans: ui.set_transcript(locus_text=answer))
                    ui.root.after(0, lambda: ui.set_status("Mood check", "success", "Gemini replied in cat mode."))
                    time.sleep(2.5)

                elif res == "gemini_request":
                    ans = ask_gemini(text)
                    ui.root.after(0, lambda answer=ans: ui.set_transcript(locus_text=answer))
                    ui.root.after(0, lambda: ui.set_status("Answered", "success", "Gemini handled the request."))
                    time.sleep(2.5)

                elif res == "success":
                    ui.root.after(0, lambda: ui.fade_to_image("success"))
                    ui.root.after(0, lambda: ui.set_status("Success!", "success", "Command executed successfully."))
                    ui.root.after(0, lambda: ui.set_transcript(locus_text="Done."))
                    time.sleep(1)

                elif res == "bye":
                    ui.root.after(0, lambda: ui.fade_to_image("success"))
                    ui.root.after(0, lambda: ui.set_status("Goodbye", "success", "Closing Locus."))
                    ui.root.after(0, ui.root.quit)
                    return

                else:
                    ui.root.after(0, lambda: ui.set_status("Not sure", "prompt", "I heard you, but I do not know that command yet."))
                    ui.root.after(0, lambda: ui.set_transcript(locus_text="I am not sure what to do with that yet."))
                    time.sleep(1.5)

        except (OSError, IOError) as mic_err:
            print(f"Microphone Error: {mic_err}")
            ui.root.after(0, ui.stop_visualizer)
            ui.root.after(0, lambda: ui.fade_to_image("error"))
            ui.root.after(0, lambda: ui.set_status("No microphone", "error", "I cannot access the microphone right now."))
            ui.root.after(0, lambda: ui.set_mic_state("error", "Check your microphone connection and permissions."))
            ui.root.after(0, lambda: ui.set_transcript(locus_text="I cannot hear you because the microphone is unavailable."))
            time.sleep(4)
            break
        except sr.WaitTimeoutError:
            print("LOG: Timeout. Sleeping.")
            break
        except sr.UnknownValueError:
            ui.root.after(0, lambda: ui.set_status("Come again?", "prompt", "I could not understand that phrase."))
            ui.root.after(0, lambda: ui.set_transcript(locus_text="Say that again for me."))
            time.sleep(1)
            continue
        except Exception as exc:
            print(f"Error: {exc}")
            ui.root.after(0, lambda: ui.set_status("Unexpected error", "error", str(exc)))
            break

    is_processing = False
    ui.root.after(0, ui.stop_visualizer)
    ui.root.after(0, lambda: ui.fade_to_image("idle"))
    ui.root.after(0, lambda: ui.set_mic_state("idle", "Ready for the next wake word."))
    ui.root.after(0, lambda: ui.set_status("Say 'Locus'", "idle", "Left-click the cat or wait for the wake word."))


def background_listener(ui):
    recognizer = sr.Recognizer()
    while True:
        if not is_processing:
            try:
                with sr.Microphone() as source:
                    audio = recognizer.listen(source, phrase_time_limit=3)
                    text = recognizer.recognize_google(audio, language=config.LANG_CODE).lower()
                    if any(wake_word in text for wake_word in config.WAKE_WORDS):
                        threading.Thread(target=listen_and_process, args=(ui,), daemon=True).start()
            except Exception:
                time.sleep(3)
        time.sleep(0.1)
