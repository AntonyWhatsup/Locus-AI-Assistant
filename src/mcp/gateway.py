"""MCP Gateway (Mediation Layer) managing multi-server connections and tool routing."""
import logging
import threading
from typing import Any, Dict, List, Optional, Tuple

from src.mcp.client import MCPClient
from src.mcp.exceptions import (
    MCPConnectionError,
    MCPError,
    MCPExecutionError,
    MCPTimeoutError,
    MCPToolNotFoundError,
)
from src.mcp.models import MCPTool, ServerConfig, ServerStatus, ToolExecutionResult
from src.mcp.registry import ServerRegistry

logger = logging.getLogger("locus.mcp.gateway")


class MCPGateway:
    """Central mediation layer routing requests between Locus and multiple MCP servers."""

    def __init__(self, registry: Optional[ServerRegistry] = None):
        self.registry = registry or ServerRegistry()
        self._clients: Dict[str, MCPClient] = {}
        self._server_statuses: Dict[str, ServerStatus] = {}
        self._tools_cache: Dict[str, List[MCPTool]] = {}
        self._lock = threading.RLock()

    def get_status(self, server_id: str) -> ServerStatus:
        with self._lock:
            return self._server_statuses.get(server_id, ServerStatus.DISCONNECTED)

    def start_server(self, server_id: str) -> bool:
        """Start or connect to a specific registered server."""
        with self._lock:
            config = self.registry.get(server_id)
            if not config:
                raise MCPError(f"Server '{server_id}' not found in registry.")

            if not config.enabled:
                logger.info("Server '%s' is disabled, skipping start.", server_id)
                return False

            client = self._clients.get(server_id)
            if client and client.is_alive:
                return True

            self._server_statuses[server_id] = ServerStatus.CONNECTING
            try:
                full_cmd = [config.command] + config.args if config.args else config.command
                client = MCPClient(
                    command=full_cmd,
                    server_id=server_id,
                    timeout_seconds=config.timeout_seconds,
                    env=config.env or None,
                )
                client.start()
                self._clients[server_id] = client
                self._server_statuses[server_id] = ServerStatus.CONNECTED
                
                # Pre-fetch tools into cache
                try:
                    self._tools_cache[server_id] = client.list_tools()
                except Exception as exc:
                    logger.warning("Could not pre-fetch tools for %s: %s", server_id, exc)

                logger.info("MCP server '%s' started successfully.", server_id)
                return True
            except Exception as exc:
                self._server_statuses[server_id] = ServerStatus.FAILED
                logger.error("Failed to start MCP server '%s': %s", server_id, exc)
                raise MCPConnectionError(f"Cannot start MCP server '{server_id}': {exc}") from exc

    def stop_server(self, server_id: str) -> None:
        """Stop a specific running server."""
        with self._lock:
            client = self._clients.pop(server_id, None)
            if client:
                try:
                    client.close()
                except Exception as exc:
                    logger.warning("Error stopping server '%s': %s", server_id, exc)
            self._server_statuses[server_id] = ServerStatus.DISCONNECTED
            self._tools_cache.pop(server_id, None)

    def start_all(self) -> Dict[str, bool]:
        """Start all enabled registered servers."""
        results = {}
        for config in self.registry.list_enabled():
            try:
                results[config.server_id] = self.start_server(config.server_id)
            except Exception as exc:
                logger.error("Error starting '%s': %s", config.server_id, exc)
                results[config.server_id] = False
        return results

    def stop_all(self) -> None:
        """Stop all currently running servers."""
        with self._lock:
            server_ids = list(self._clients.keys())
            for server_id in server_ids:
                self.stop_server(server_id)

    def list_all_tools(self) -> List[MCPTool]:
        """Aggregate available tools from all enabled and running servers."""
        with self._lock:
            all_tools: List[MCPTool] = []
            for config in self.registry.list_enabled():
                server_id = config.server_id
                client = self._clients.get(server_id)
                if not client or not client.is_alive:
                    try:
                        self.start_server(server_id)
                        client = self._clients.get(server_id)
                    except Exception:
                        continue

                if client and client.is_alive:
                    try:
                        tools = client.list_tools()
                        self._tools_cache[server_id] = tools
                        all_tools.extend(tools)
                    except Exception as exc:
                        logger.warning("Error listing tools for '%s': %s", server_id, exc)
                        cached = self._tools_cache.get(server_id, [])
                        all_tools.extend(cached)
            return all_tools

    def resolve_tool(self, tool_name: str, server_id: Optional[str] = None) -> Tuple[str, str]:
        """Resolve a tool name into (server_id, actual_tool_name).
        
        Supports formats:
        - explicit server: 'project__status' -> ('project', 'status')
        - namespaced colon: 'project:status' -> ('project', 'status')
        - bare name with explicit server_id
        - bare name searching across all registered servers
        """
        raw_name = str(tool_name).strip()

        # 1. Explicit delimiter in tool_name
        if "__" in raw_name:
            prefix, actual = raw_name.split("__", 1)
            if self.registry.get(prefix):
                return prefix, actual
        elif ":" in raw_name:
            prefix, actual = raw_name.split(":", 1)
            if self.registry.get(prefix):
                return prefix, actual

        # 2. Explicit server_id provided
        if server_id and self.registry.get(server_id):
            return server_id, raw_name

        # 3. Search across cached or running tools
        with self._lock:
            all_tools = self.list_all_tools()
            for tool in all_tools:
                if tool.name == raw_name:
                    return tool.server_id, tool.name

        raise MCPToolNotFoundError(f"MCP tool '{tool_name}' could not be resolved to any active server.")

    def execute_tool(
        self,
        tool_name: str,
        arguments: Optional[Dict[str, Any]] = None,
        server_id: Optional[str] = None,
    ) -> ToolExecutionResult:
        """Execute a tool through the mediation layer with full error containment."""
        try:
            target_server, actual_tool = self.resolve_tool(tool_name, server_id=server_id)
        except MCPError as exc:
            return ToolExecutionResult(
                tool_name=tool_name,
                server_id=server_id or "unknown",
                success=False,
                error=str(exc),
            )

        with self._lock:
            client = self._clients.get(target_server)
            if not client or not client.is_alive:
                try:
                    self.start_server(target_server)
                    client = self._clients.get(target_server)
                except Exception as exc:
                    return ToolExecutionResult(
                        tool_name=actual_tool,
                        server_id=target_server,
                        success=False,
                        error=f"Server '{target_server}' connection failed: {exc}",
                    )

        if not client:
            return ToolExecutionResult(
                tool_name=actual_tool,
                server_id=target_server,
                success=False,
                error=f"No active client for server '{target_server}'.",
            )

        try:
            output = client.call_tool(actual_tool, arguments=arguments)
            return ToolExecutionResult(
                tool_name=actual_tool,
                server_id=target_server,
                success=True,
                content=output,
            )
        except MCPExecutionError as exc:
            return ToolExecutionResult(
                tool_name=actual_tool,
                server_id=target_server,
                success=False,
                error=f"Tool execution failed: {exc}",
            )
        except MCPTimeoutError as exc:
            return ToolExecutionResult(
                tool_name=actual_tool,
                server_id=target_server,
                success=False,
                error=f"Tool execution timed out: {exc}",
            )
        except Exception as exc:
            return ToolExecutionResult(
                tool_name=actual_tool,
                server_id=target_server,
                success=False,
                error=f"Unexpected error executing tool: {exc}",
            )

    def call_tool_text(
        self,
        tool_name: str,
        arguments: Optional[Dict[str, Any]] = None,
        server_id: Optional[str] = None,
    ) -> str:
        """Convenience method returning string output or raising MCPError (backward compatible)."""
        result = self.execute_tool(tool_name, arguments=arguments, server_id=server_id)
        if not result.success:
            raise MCPError(result.error or f"Failed to call MCP tool '{tool_name}'")
        return result.content or ""
