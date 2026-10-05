"""Backward-compatible proxy module for src.mcp.

This module ensures existing imports from `src.mcp_client` continue to work seamlessly
while delegating core logic to the modular `src.mcp` package.
"""
from src.mcp import (
    DEFAULT_PROTOCOL_VERSION,
    DEFAULT_TIMEOUT_SECONDS,
    MCPClient,
    MCPError,
    MCPTool,
    call_mcp_tool,
)

__all__ = [
    "DEFAULT_PROTOCOL_VERSION",
    "DEFAULT_TIMEOUT_SECONDS",
    "MCPClient",
    "MCPError",
    "MCPTool",
    "call_mcp_tool",
]
