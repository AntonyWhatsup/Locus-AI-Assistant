"""Low-level MCP Client handling individual server stdio communication."""
import contextlib
import json
import queue
import shlex
import subprocess
import threading
from typing import Any, Dict, List, Optional, Union

from src.mcp.exceptions import (
    MCPConnectionError,
    MCPError,
    MCPExecutionError,
    MCPTimeoutError,
    MCPToolNotFoundError,
)
from src.mcp.models import MCPTool

DEFAULT_PROTOCOL_VERSION = "2025-06-18"
DEFAULT_TIMEOUT_SECONDS = 8.0


class MCPClient:
    """Client for communicating with a single MCP server over stdio."""

    def __init__(
        self,
        command: Union[str, List[str]],
        server_id: str = "default",
        timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
        env: Optional[Dict[str, str]] = None,
    ):
        self.command = self._normalize_command(command)
        self.server_id = str(server_id or "default")
        self.timeout_seconds = float(timeout_seconds)
        self.env = env
        self._process: Optional[subprocess.Popen] = None
        self._stdout_queue: queue.Queue = queue.Queue()
        self._stderr_queue: queue.Queue = queue.Queue()
        self._next_id: int = 1
        self._is_initialized: bool = False
        self._lock = threading.RLock()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    @property
    def is_alive(self) -> bool:
        return self._process is not None and self._process.poll() is None

    def start(self):
        with self._lock:
            if self.is_alive:
                return

            try:
                self._process = subprocess.Popen(
                    self.command,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    encoding="utf-8",
                    bufsize=1,
                    env=self.env,
                )
            except OSError as exc:
                raise MCPConnectionError(f"Failed to start MCP server [{self.server_id}]: {exc}") from exc

            threading.Thread(
                target=self._pump_stream,
                args=(self._process.stdout, self._stdout_queue),
                daemon=True,
            ).start()
            threading.Thread(
                target=self._pump_stream,
                args=(self._process.stderr, self._stderr_queue),
                daemon=True,
            ).start()

            self.initialize()

    def close(self):
        with self._lock:
            process = self._process
            self._process = None
            self._is_initialized = False
            if process is None:
                return

            try:
                if process.stdin:
                    process.stdin.close()
            except OSError:
                pass

            try:
                process.terminate()
                process.wait(timeout=1.5)
            except Exception:
                with contextlib.suppress(Exception):
                    process.kill()
                with contextlib.suppress(Exception):
                    process.wait(timeout=1.0)
            finally:
                for stream in (process.stdout, process.stderr):
                    with contextlib.suppress(Exception):
                        if stream:
                            stream.close()

    def initialize(self) -> Dict[str, Any]:
        response = self._request(
            "initialize",
            {
                "protocolVersion": DEFAULT_PROTOCOL_VERSION,
                "capabilities": {},
                "clientInfo": {"name": "locus", "version": "0.1.0"},
            },
        )
        self._notify("notifications/initialized", {})
        self._is_initialized = True
        return response

    def list_tools(self) -> List[MCPTool]:
        response = self._request("tools/list", {})
        tools = response.get("tools", [])
        return [
            MCPTool(
                name=str(tool.get("name", "")),
                description=str(tool.get("description", "")),
                input_schema=dict(tool.get("inputSchema") or {}),
                server_id=self.server_id,
            )
            for tool in tools
            if tool.get("name")
        ]

    def call_tool(self, name: str, arguments: Optional[Dict[str, Any]] = None) -> str:
        response = self._request(
            "tools/call",
            {"name": str(name), "arguments": dict(arguments or {})},
        )
        if response.get("isError"):
            error_msg = self._extract_text_content(response) or f"Tool call failed: {name}"
            raise MCPExecutionError(error_msg)
        return self._extract_text_content(response)

    def has_tool(self, name: str) -> bool:
        return any(tool.name == name for tool in self.list_tools())

    @staticmethod
    def _normalize_command(command: Union[str, List[str]]) -> List[str]:
        if isinstance(command, (list, tuple)):
            normalized = [str(part).strip() for part in command if str(part).strip()]
        else:
            raw_command = str(command or "").strip()
            try:
                normalized = shlex.split(raw_command, posix=True)
            except ValueError:
                normalized = shlex.split(raw_command, posix=False)
        if not normalized:
            raise MCPError("MCP server command is not configured.")
        return normalized

    @staticmethod
    def _pump_stream(stream, output_queue: queue.Queue):
        if stream is None:
            return
        for line in iter(stream.readline, ""):
            output_queue.put(line.rstrip("\r\n"))

    @staticmethod
    def _extract_text_content(response: Dict[str, Any]) -> str:
        content = response.get("content", [])
        text_parts = []
        for item in content:
            if item.get("type") == "text":
                text = str(item.get("text", "")).strip()
                if text:
                    text_parts.append(text)
        return "\n".join(text_parts).strip()

    def _request(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        with self._lock:
            request_id = self._next_id
            self._next_id += 1

            self._send_message(
                {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "method": method,
                    "params": params,
                }
            )

            while True:
                message = self._read_message()
                if message.get("id") != request_id:
                    continue
                if "error" in message:
                    raise MCPExecutionError(self._format_error(message["error"]))
                return dict(message.get("result") or {})

    def _notify(self, method: str, params: Dict[str, Any]):
        self._send_message(
            {
                "jsonrpc": "2.0",
                "method": method,
                "params": params,
            }
        )

    def _send_message(self, payload: Dict[str, Any]):
        if self._process is None or self._process.stdin is None:
            raise MCPConnectionError("MCP server is not running.")

        try:
            self._process.stdin.write(json.dumps(payload) + "\n")
            self._process.stdin.flush()
        except OSError as exc:
            raise MCPConnectionError(f"Failed to send MCP message: {exc}") from exc

    def _read_message(self) -> Dict[str, Any]:
        if self._process is not None and self._process.poll() is not None:
            stderr_text = self._drain_stderr()
            raise MCPConnectionError(f"MCP server exited unexpectedly. {stderr_text}".strip())

        try:
            line = self._stdout_queue.get(timeout=self.timeout_seconds)
        except queue.Empty as exc:
            stderr_text = self._drain_stderr()
            raise MCPTimeoutError(f"MCP server timed out after {self.timeout_seconds}s. {stderr_text}".strip()) from exc

        if not line:
            return self._read_message()

        try:
            return json.loads(line)
        except json.JSONDecodeError as exc:
            raise MCPError(f"Invalid MCP JSON response: {line}") from exc

    def _drain_stderr(self) -> str:
        lines = []
        while True:
            try:
                lines.append(self._stderr_queue.get_nowait())
            except queue.Empty:
                break
        text = " ".join(part.strip() for part in lines if part.strip())
        return f"stderr: {text}" if text else ""

    @staticmethod
    def _format_error(error: Any) -> str:
        if isinstance(error, dict):
            message = str(error.get("message", "Unknown MCP error")).strip()
            code = error.get("code")
            return f"{message} (code: {code})" if code is not None else message
        return str(error)
