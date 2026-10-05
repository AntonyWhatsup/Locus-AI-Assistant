"""Model Context Protocol (MCP) Subsystem for Locus AI Assistant."""
import threading
from pathlib import Path
from typing import Any, Dict, Optional

import src.config as config
from src.mcp.client import MCPClient
from src.mcp.exceptions import (
    MCPConnectionError,
    MCPError,
    MCPExecutionError,
    MCPTimeoutError,
    MCPToolNotFoundError,
)
from src.mcp.gateway import MCPGateway
from src.mcp.models import (
    MCPTool,
    RiskLevel,
    ServerConfig,
    ServerStatus,
    ServerTransport,
    ToolExecutionResult,
)
from src.mcp.registry import ServerRegistry

DEFAULT_PROTOCOL_VERSION = "2025-06-18"
DEFAULT_TIMEOUT_SECONDS = 8.0

_global_gateway: Optional[MCPGateway] = None
_gateway_lock = threading.Lock()


def get_gateway() -> MCPGateway:
    """Return the global shared MCPGateway instance, initializing if needed."""
    global _global_gateway
    with _gateway_lock:
        if _global_gateway is None:
            registry = ServerRegistry()
            servers_json = Path(__file__).resolve().parents[2] / "data" / "mcp_servers.json"
            if servers_json.exists():
                registry.load_from_file(servers_json)

            # If legacy MCP_SERVER_COMMAND is specified and enabled, ensure default server is registered
            if getattr(config, "MCP_ENABLED", False) and getattr(config, "MCP_SERVER_COMMAND", ""):
                registry.register(
                    ServerConfig(
                        server_id="default",
                        command=config.MCP_SERVER_COMMAND,
                        enabled=True,
                    )
                )

            _global_gateway = MCPGateway(registry=registry)
        return _global_gateway


def reset_gateway() -> None:
    """Reset and stop the global MCP gateway (useful for testing)."""
    global _global_gateway
    with _gateway_lock:
        if _global_gateway is not None:
            _global_gateway.stop_all()
            _global_gateway = None


def call_mcp_tool(
    command_or_tool: str,
    tool_name: Optional[str] = None,
    arguments: Optional[Dict[str, Any]] = None,
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
) -> str:
    """Backward-compatible function to invoke an MCP tool.
    
    Can be called as:
      call_mcp_tool(command, tool_name, arguments, timeout_seconds)
    Or as:
      call_mcp_tool("tool_name", arguments=...)
    """
    if tool_name is not None:
        # Legacy signature: command, tool_name
        command = command_or_tool
        with MCPClient(command=command, timeout_seconds=timeout_seconds) as client:
            if not client.has_tool(tool_name):
                raise MCPError(f"MCP tool not found: {tool_name}")
            return client.call_tool(tool_name, arguments=arguments)
    else:
        # Gateway-based signature: tool_name
        gateway = get_gateway()
        return gateway.call_tool_text(command_or_tool, arguments=arguments)


__all__ = [
    "DEFAULT_PROTOCOL_VERSION",
    "DEFAULT_TIMEOUT_SECONDS",
    "MCPClient",
    "MCPError",
    "MCPConnectionError",
    "MCPTimeoutError",
    "MCPToolNotFoundError",
    "MCPExecutionError",
    "MCPTool",
    "RiskLevel",
    "ServerConfig",
    "ServerStatus",
    "ServerTransport",
    "ToolExecutionResult",
    "ServerRegistry",
    "MCPGateway",
    "get_gateway",
    "reset_gateway",
    "call_mcp_tool",
]
