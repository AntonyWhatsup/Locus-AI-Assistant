import audioop
import threading
import time
from contextlib import suppress

import speech_recognition as sr
import torch

import src.config as config
from src.actions import ask_gemini, ask_mcp, execute_command_logic
from src.brain.model import NeuralNet
from src.brain.nltk_utils import bag_of_words, tokenize


device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model, all_words, tags = None, None, None
active_context = None

_MODEL_LOCK = threading.Lock()
_PROCESSING_LOCK = threading.Lock()
_is_processing = False
_cancel_event = threading.Event()


class ListeningCancelled(Exception):
    pass


def _set_processing(value):
    global _is_processing
    with _PROCESSING_LOCK:
        _is_processing = value


def is_processing():
    with _PROCESSING_LOCK:
        return _is_processing


def try_begin_processing():
    with _PROCESSING_LOCK:
        global _is_processing
        if _is_processing:
            return False
        _is_processing = True
        return True


def finish_processing():
    _set_processing(False)


def clear_active_context():
    global active_context
    active_context = None


def reload_model():
    """Load the trained model from disk."""
    global model, all_words, tags
    try:
        data = torch.load(config.MODEL_DATA_PATH, map_location=device, weights_only=True)
        required_keys = {"model_state", "input_size", "hidden_size", "output_size", "all_words", "tags"}
        if not isinstance(data, dict) or not required_keys.issubset(data):
            raise ValueError("Model file is missing required fields.")

        loaded_model = NeuralNet(data["input_size"], data["hidden_size"], data["output_size"]).to(device)
        loaded_model.load_state_dict(data["model_state"])
        loaded_model.eval()

        with _MODEL_LOCK:
            model = loaded_model
            all_words = list(data["all_words"])
            tags = list(data["tags"])
        print("LOG: Brain reloaded.")
        return True
    except Exception as exc:
        print(f"Reload Error: {exc}")
        with _MODEL_LOCK:
            model, all_words, tags = None, None, None
        return False


def manual_activation(ui):
    """Manually trigger listening."""
    if not try_begin_processing():
        getattr(ui, "command_ack", lambda *_args: None)("listen", False, "A listening session is already active.")
        return False
    _cancel_event.clear()
    print("LOG: Manual activation via click.")
    threading.Thread(target=listen_and_process, args=(ui,), daemon=True).start()
    getattr(ui, "command_ack", lambda *_args: None)("listen", True, "Listening started.")
    return True


def stop_activation(ui):
    """Request cooperative cancellation of the active listening session."""
    if not is_processing():
        getattr(ui, "command_ack", lambda *_args: None)("stop", False, "No listening session is active.")
        return False
    _cancel_event.set()
    ui.root.after(0, ui.stop_visualizer)
    ui.root.after(0, lambda: ui.set_mic_state("idle", "Stopping listening..."))
    ui.root.after(0, lambda: ui.set_status("Stopping", "thinking", "Stopping the current request."))
    getattr(ui, "command_ack", lambda *_args: None)("stop", True, "Stop requested.")
    return True


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
        if _cancel_event.is_set():
            raise ListeningCancelled()
        chunks.append(chunk.frame_data)
        level = _normalize_level(chunk.frame_data, chunk.sample_width)
        ui.root.after(0, lambda lvl=level: ui.update_mic_level(lvl))

    if not chunks:
        raise sr.UnknownValueError()

    return sr.AudioData(b"".join(chunks), source.SAMPLE_RATE, source.SAMPLE_WIDTH)


def _resolve_microphone_device_index():
    saved_device_id = str(config.MICROPHONE_DEVICE_ID).strip()
    if not saved_device_id:
        return None

    try:
        device_names = sr.Microphone.list_microphone_names()
    except Exception:
        return None

    for index, device_name in enumerate(device_names):
        if str(device_name).strip() == saved_device_id:
            return index
    return None


def _open_microphone():
    return sr.Microphone(device_index=_resolve_microphone_device_index())


def _classify_text(text):
    with _MODEL_LOCK:
        if model is None or all_words is None or tags is None:
            raise RuntimeError("Local model is not loaded.")

        encoded = bag_of_words(tokenize(text), all_words).reshape(1, -1)
        tensor = torch.from_numpy(encoded).to(device)
        with torch.inference_mode():
            output = model(tensor)
            probabilities = torch.softmax(output, dim=1)
            prob, predicted = torch.max(probabilities, dim=1)
        tag = tags[predicted.item()]
        return tag, prob.item()


def _restore_idle_ui(ui):
    ui.root.after(0, ui.stop_visualizer)
    ui.root.after(0, lambda: ui.fade_to_image("idle"))
    ui.root.after(0, lambda: ui.set_mic_state("idle", "Ready for the next wake word."))
    if config.CLOUD_WAKE_LISTENER_ENABLED:
        ui.root.after(0, lambda: ui.set_status("Say 'Locus'", "idle", "Click the cat or wait for the wake word."))
    else:
        ui.root.after(0, lambda: ui.set_status("Click to listen", "idle", "Cloud wake-word listening is disabled by default."))


def _handle_microphone_error(ui, mic_err):
    print(f"Microphone Error: {mic_err}")
    ui.root.after(0, ui.stop_visualizer)
    ui.root.after(0, lambda: ui.fade_to_image("error"))
    ui.root.after(0, lambda: ui.set_status("No microphone", "error", "I cannot access the microphone right now."))
    ui.root.after(0, lambda: ui.set_mic_state("error", "Check your microphone connection and permissions."))
    ui.root.after(0, lambda: ui.set_transcript(locus_text="I cannot hear you because the microphone is unavailable."))
    time.sleep(4)


def _handle_unknown_phrase(ui):
    ui.root.after(0, lambda: ui.set_status("Come again?", "prompt", "I could not understand that phrase."))
    ui.root.after(0, lambda: ui.set_transcript(locus_text="Say that again for me."))
    time.sleep(1)


def _handle_unexpected_error(ui, exc):
    print(f"Error: {exc}")
    ui.root.after(0, ui.stop_visualizer)
    ui.root.after(0, lambda: ui.fade_to_image("error"))
    ui.root.after(0, lambda: ui.set_mic_state("error", "An unexpected error interrupted listening."))
    ui.root.after(0, lambda: ui.set_status("Unexpected error", "error", "The current request could not be completed."))
    ui.root.after(0, lambda: ui.set_transcript(locus_text="Something went wrong while processing that request."))


def listen_and_process(ui):
    global active_context
    clear_context_on_exit = False
    try:
        with _MODEL_LOCK:
            model_ready = model is not None and all_words is not None and tags is not None

        if not model_ready:
            ui.root.after(0, lambda: ui.set_status("Brain not ready", "prompt", "Wait until training finishes, then try again."))
            ui.root.after(0, lambda: ui.set_transcript(locus_text="The local model is still loading."))
            return

        recognizer = sr.Recognizer()
        recognizer.pause_threshold = 1.0

        while True:
            if _cancel_event.is_set():
                raise ListeningCancelled()
            if active_context:
                ui.root.after(0, lambda: ui.set_status("Which profile?", "prompt", "Choose a Chrome profile to continue."))
                ui.root.after(0, lambda: ui.fade_to_image("think"))
                ui.root.after(0, lambda: ui.set_mic_state("listening", "Waiting for your profile answer..."))
                ui.root.after(0, lambda: ui.start_visualizer("Waiting for your profile answer..."))
            else:
                ui.root.after(0, lambda: ui.set_status("Listening...", "listening", "Speak after the cat changes state."))
                ui.root.after(0, lambda: ui.fade_to_image("listen"))
                ui.root.after(0, ui.start_visualizer)

            try:
                with _open_microphone() as source:
                    with suppress(Exception):
                        recognizer.adjust_for_ambient_noise(source, duration=0.2)

                    audio = _capture_phrase(recognizer, source, ui)
                    if _cancel_event.is_set():
                        raise ListeningCancelled()
                    ui.root.after(0, ui.stop_visualizer)

                    ui.root.after(0, lambda: ui.set_status("Thinking...", "thinking", "Processing your request..."))
                    ui.root.after(0, lambda: ui.set_mic_state("thinking", "Processing your request..."))
                    ui.root.after(0, lambda: ui.fade_to_image("think"))

                    text = recognizer.recognize_google(audio, language=config.LANG_CODE).strip()
                    if _cancel_event.is_set():
                        raise ListeningCancelled()
                    if not text:
                        raise sr.UnknownValueError()
                    ui.root.after(0, lambda captured=text: ui.set_transcript(user_text=captured))

                    tag, conf = _classify_text(text)
                    print(f"LOG: Heard '{text}' -> {tag} ({conf:.2f})")

                    result, active_context = execute_command_logic(tag, conf, active_context)

                    if result == "ask_profile_yt":
                        ui.root.after(0, lambda: ui.set_status("Which YouTube profile?", "prompt", "Answer with Anton, Clean, or Default."))
                        ui.root.after(0, lambda: ui.set_transcript(locus_text="Anton, Clean, or Default?"))
                        time.sleep(0.5)
                        continue

                    if result == "ask_profile_chrome":
                        ui.root.after(0, lambda: ui.set_status("Which Chrome profile?", "prompt", "Answer with Anton, Clean, or Default."))
                        ui.root.after(0, lambda: ui.set_transcript(locus_text="Please choose an account."))
                        time.sleep(0.5)
                        continue

                    if result == "think":
                        ui.root.after(0, lambda: ui.set_status("Still waiting", "prompt", "Answer with Anton, Clean, or Default."))
                        ui.root.after(0, lambda: ui.set_transcript(locus_text="I still need the profile name: Anton, Clean, or Default."))
                        time.sleep(0.8)
                        continue

                    if result == "gemini_cool_request":
                        ui.root.after(0, lambda: ui.fade_to_image("cool"))
                        answer = ask_gemini(f"Answer cool and short: {text}")
                        ui.root.after(0, lambda answer_text=answer: ui.set_transcript(locus_text=answer_text))
                        ui.root.after(0, lambda: ui.set_status("Mood check", "success", "Gemini replied in cat mode."))
                        time.sleep(2.5)
                        break

                    if result == "gemini_request":
                        answer = ask_gemini(text)
                        ui.root.after(0, lambda answer_text=answer: ui.set_transcript(locus_text=answer_text))
                        ui.root.after(0, lambda: ui.set_status("Answered", "success", "Gemini handled the request."))
                        time.sleep(2.5)
                        break

                    if result == "mcp_status_request":
                        answer = ask_mcp(tool_name="project_status")
                        ui.root.after(0, lambda answer_text=answer: ui.set_transcript(locus_text=answer_text))
                        ui.root.after(0, lambda: ui.set_status("MCP answered", "success", "The configured MCP tool returned a result."))
                        time.sleep(2.5)
                        break

                    if result == "mcp_request":
                        answer = ask_mcp(text=text)
                        ui.root.after(0, lambda answer_text=answer: ui.set_transcript(locus_text=answer_text))
                        ui.root.after(0, lambda: ui.set_status("MCP answered", "success", "The configured MCP tool returned a result."))
                        time.sleep(2.5)
                        break

                    if result == "success":
                        ui.root.after(0, lambda: ui.fade_to_image("success"))
                        ui.root.after(0, lambda: ui.set_status("Success!", "success", "Command executed successfully."))
                        ui.root.after(0, lambda: ui.set_transcript(locus_text="Done."))
                        time.sleep(1)
                        break

                    if result == "error":
                        ui.root.after(0, lambda: ui.fade_to_image("error"))
                        ui.root.after(0, lambda: ui.set_status("Action failed", "error", "I could not open the requested target."))
                        ui.root.after(0, lambda: ui.set_transcript(locus_text="I could not launch that right now."))
                        time.sleep(1.5)
                        break

                    if result == "bye":
                        ui.root.after(0, lambda: ui.fade_to_image("success"))
                        ui.root.after(0, lambda: ui.set_status("Goodbye", "success", "Closing Locus."))
                        ui.root.after(0, ui.root.quit)
                        return

                    ui.root.after(0, lambda: ui.set_status("Not sure", "prompt", "I heard you, but I do not know that command yet."))
                    ui.root.after(0, lambda: ui.set_transcript(locus_text="I am not sure what to do with that yet."))
                    time.sleep(1.5)
                    break

            except (OSError, IOError) as mic_err:
                _handle_microphone_error(ui, mic_err)
                break
            except sr.WaitTimeoutError:
                print("LOG: Listening timed out.")
                clear_context_on_exit = True
                break
            except sr.UnknownValueError:
                _handle_unknown_phrase(ui)
                continue
            except ListeningCancelled:
                print("LOG: Listening stopped by user.")
                clear_context_on_exit = True
                break
            except Exception as exc:
                _handle_unexpected_error(ui, exc)
                clear_context_on_exit = True
                break
    finally:
        if clear_context_on_exit:
            clear_active_context()
        finish_processing()
        _cancel_event.clear()
        _restore_idle_ui(ui)


def background_listener(ui):
    if not config.CLOUD_WAKE_LISTENER_ENABLED:
        return

    recognizer = sr.Recognizer()
    recognizer.pause_threshold = 0.8

    while True:
        if is_processing():
            time.sleep(0.2)
            continue

        try:
            with _open_microphone() as source:
                with suppress(Exception):
                    recognizer.adjust_for_ambient_noise(source, duration=0.2)

                audio = recognizer.listen(source, timeout=1, phrase_time_limit=3)
                text = recognizer.recognize_google(audio, language=config.LANG_CODE).lower()
        except sr.WaitTimeoutError:
            continue
        except Exception:
            time.sleep(2)
            continue

        if any(wake_word in text for wake_word in config.WAKE_WORDS) and try_begin_processing():
            threading.Thread(target=listen_and_process, args=(ui,), daemon=True).start()
        else:
            time.sleep(0.1)
