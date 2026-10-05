"""Data models for Model Context Protocol (MCP) subsystem."""
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class ServerTransport(str, Enum):
    STDIO = "stdio"
    SSE = "sse"


class RiskLevel(str, Enum):
    SAFE_READ = "safe_read"
    DESTRUCTIVE_WRITE = "destructive_write"
    SYSTEM_EXEC = "system_exec"
    NETWORK_TRANSMIT = "network_transmit"


class ServerStatus(str, Enum):
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    FAILED = "failed"


@dataclass(frozen=True)
class MCPTool:
    name: str
    description: str
    input_schema: Dict[str, Any] = field(default_factory=dict)
    server_id: str = "default"
    risk_level: RiskLevel = RiskLevel.SAFE_READ

    @property
    def qualified_name(self) -> str:
        """Returns namespaced tool identifier: server_id__tool_name."""
        if self.server_id and self.server_id != "default":
            return f"{self.server_id}__{self.name}"
        return self.name


@dataclass
class ServerConfig:
    server_id: str
    command: str
    args: List[str] = field(default_factory=list)
    env: Dict[str, str] = field(default_factory=dict)
    enabled: bool = True
    transport: ServerTransport = ServerTransport.STDIO
    timeout_seconds: float = 8.0
    auto_restart: bool = True
    max_retries: int = 2


@dataclass
class ToolExecutionResult:
    tool_name: str
    server_id: str
    success: bool
    content: Optional[str] = None
    error: Optional[str] = None
    raw_payload: Optional[Dict[str, Any]] = None
