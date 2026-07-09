# User Guide

## Purpose

Locus is a desktop voice assistant with a cat-themed interface. It listens for a wake word, handles a small set of commands locally, and sends other requests to Google Gemini.

## Before You Start

- Python 3.10 or newer
- Windows
- A working microphone
- A `.env` file with `GEMINI_KEY`

## Starting the App

Run:

```powershell
python main.py
```

Startup flow:

1. The Tkinter window opens.
2. The local intent model retrains from `src/brain/intents.json`.
3. The new model is loaded.
4. The UI returns to idle.
5. Background wake-word listening begins.

## How To Activate Locus

- Say `Locus`
- Similar words may also trigger it: `local`, `locust`, `focus`
- Left-click the cat image to manually start listening

## Supported Commands

| Phrase | Result |
|---|---|
| `Open browser` or `Start Chrome` | Prompts for a Chrome profile and opens Chrome |
| `Open YouTube` | Prompts for a Chrome profile and opens YouTube |
| `Anton`, `Anthony`, `Tony` | Selects the Anton profile |
| `Clean`, `Mr Clean` | Selects the Mr Clean profile |
| `Default`, `Normal`, `Main` | Selects the default profile |
| `How are you?` | Sends a short playful request to Gemini |
| `Bye`, `Goodbye`, `Exit` | Closes the application |
| Other recognized speech | Sent to Gemini for a short response |

## UI States

| State | Meaning |
|---|---|
| `idle` | Waiting for the wake word |
| `listen` | Capturing voice input |
| `think` | Processing speech or waiting for profile selection |
| `train` | Retraining the local model |
| `cool` | Handling a casual Gemini-style response |
| `success` | Command completed |
| `error` | Audio or microphone issue |

## Troubleshooting

- If the microphone fails, verify device access and Windows audio permissions.
- If Gemini replies fail, confirm `GEMINI_KEY` is set correctly in `.env`.
- If Chrome does not open, check the profile mapping in `src/config.py`.
- If the app does not recognize expected commands, review `src/brain/intents.json`.

## Where To Edit Behavior

- Intent phrases: `src/brain/intents.json`
- Runtime config defaults: `src/config.py`
- Command handling: `src/actions.py`
- Voice processing: `src/processor.py`
- UI behavior: `src/ui_manager.py`
