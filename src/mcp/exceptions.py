"""Exception hierarchy for the MCP subsystem."""

class MCPError(RuntimeError):
    """Base exception for all MCP-related errors."""


class MCPConnectionError(MCPError):
    """Raised when connection to an MCP server cannot be established or maintained."""


class MCPTimeoutError(MCPError):
    """Raised when an MCP operation exceeds its timeout budget."""


class MCPToolNotFoundError(MCPError):
    """Raised when requested tool does not exist on target server."""


class MCPExecutionError(MCPError):
    """Raised when MCP server returns an execution error during tool call."""
