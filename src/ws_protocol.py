import os
import secrets
from dataclasses import asdict, dataclass
from typing import Any, Literal

from fastapi import WebSocket


AppState = Literal["initializing", "ready", "listening", "processing", "speaking", "error"]
StatusTone = Literal["idle", "listening", "thinking", "speaking", "success", "prompt", "error"]
CommandName = Literal["listen", "stop"]


@dataclass(frozen=True)
class StatusEvent:
    type: Literal["status"]
    title: str
    tone: StatusTone
    text: str


@dataclass(frozen=True)
class MicStateEvent:
    type: Literal["mic_state"]
    state: StatusTone
    msg: str


@dataclass(frozen=True)
class TranscriptEvent:
    type: Literal["transcript"]
    user_text: str | None = None
    locus_text: str | None = None


@dataclass(frozen=True)
class ImageEvent:
    type: Literal["image"]
    image: str


@dataclass(frozen=True)
class MicLevelEvent:
    type: Literal["mic_level"]
    level: float


@dataclass(frozen=True)
class VisualizerEvent:
    type: Literal["visualizer"]
    state: Literal["start", "stop"]
    text: str | None = None


@dataclass(frozen=True)
class CommandAckEvent:
    type: Literal["command_ack"]
    action: CommandName
    accepted: bool
    state: AppState
    message: str


@dataclass(frozen=True)
class ErrorEvent:
    type: Literal["error"]
    code: str
    message: str


@dataclass(frozen=True)
class RuntimeState:
    app_state: AppState = "initializing"
    status: StatusEvent = StatusEvent(
        type="status",
        title="Starting",
        tone="thinking",
        text="Preparing the local backend.",
    )
    mic_state: MicStateEvent = MicStateEvent(
        type="mic_state",
        state="thinking",
        msg="Preparing the local backend.",
    )
    image: str = "train"
    mic_level: float = 0.0
    visualizer: VisualizerEvent = VisualizerEvent(type="visualizer", state="stop")
    user_text: str | None = None
    locus_text: str | None = None
    theme: str = "glass-green"


def event_to_dict(event: object) -> dict[str, Any]:
    return asdict(event)


def make_snapshot(state: RuntimeState) -> dict[str, Any]:
    return {
        "type": "snapshot",
        "state": state.app_state,
        "status": event_to_dict(state.status),
        "mic_state": event_to_dict(state.mic_state),
        "image": state.image,
        "mic_level": state.mic_level,
        "visualizer": event_to_dict(state.visualizer),
        "transcript": {
            "user_text": state.user_text,
            "locus_text": state.locus_text,
        },
        "settings": {
            "theme": state.theme,
        },
    }


def normalize_theme(value: object) -> str:
    normalized = str(value or "").strip().replace("_", "-").lower()
    aliases = {
        "glass-green": "glass-green",
        "glassgreen": "glass-green",
        "dark": "dark",
        "light": "light",
        "colorful": "colorful",
        "nyan": "cat",
        "cat": "cat",
    }
    return aliases.get(normalized, "glass-green")


def generate_session_token() -> str:
    return os.getenv("LOCUS_WS_TOKEN") or secrets.token_urlsafe(32)


def allowed_origins() -> set[str]:
    port = os.getenv("LOCUS_PORT", "8000")
    defaults = {
        f"http://127.0.0.1:{port}",
        f"http://localhost:{port}",
        "http://127.0.0.1:8443",
        "http://localhost:8443",
    }
    configured = {
        item.strip().rstrip("/")
        for item in os.getenv("LOCUS_ALLOWED_WS_ORIGINS", "").split(",")
        if item.strip()
    }
    return defaults | configured


def is_allowed_origin(websocket: WebSocket) -> bool:
    origin = websocket.headers.get("origin")
    if not origin:
        return True
    return origin.rstrip("/") in allowed_origins()


def validate_command(payload: Any) -> tuple[CommandName | None, str | None]:
    if not isinstance(payload, dict):
        return None, "Message must be a JSON object."

    action = payload.get("action")
    if action not in {"listen", "stop"}:
        return None, "Unknown action."

    extra_keys = set(payload) - {"action"}
    if extra_keys:
        return None, "Unsupported command fields."

    return action, None
