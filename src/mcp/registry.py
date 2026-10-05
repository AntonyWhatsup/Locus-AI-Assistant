"""Server registry for configuring and managing multiple MCP servers."""
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from src.mcp.models import RiskLevel, ServerConfig, ServerTransport

logger = logging.getLogger("locus.mcp.registry")


class ServerRegistry:
    """Registry holding configuration for multiple MCP servers."""

    def __init__(self):
        self._configs: Dict[str, ServerConfig] = {}

    def register(self, config: ServerConfig) -> None:
        """Register or update a server configuration."""
        if not config.server_id:
            raise ValueError("ServerConfig must have a non-empty server_id.")
        self._configs[config.server_id] = config
        logger.info("Registered MCP server config: %s", config.server_id)

    def unregister(self, server_id: str) -> Optional[ServerConfig]:
        """Remove a server configuration by ID."""
        return self._configs.pop(server_id, None)

    def get(self, server_id: str) -> Optional[ServerConfig]:
        """Get server configuration by ID."""
        return self._configs.get(server_id)

    def list_all(self) -> List[ServerConfig]:
        """Return all registered configurations."""
        return list(self._configs.values())

    def list_enabled(self) -> List[ServerConfig]:
        """Return only configurations that are currently enabled."""
        return [cfg for cfg in self._configs.values() if cfg.enabled]

    def load_from_dict(self, data: Dict[str, Any]) -> None:
        """Load multiple server configs from a dictionary representation."""
        servers = data.get("servers", data)
        if isinstance(servers, dict):
            for server_id, cfg_dict in servers.items():
                if isinstance(cfg_dict, dict):
                    self._parse_and_register(server_id, cfg_dict)
        elif isinstance(servers, list):
            for item in servers:
                if isinstance(item, dict) and "server_id" in item:
                    self._parse_and_register(item["server_id"], item)

    def _parse_and_register(self, server_id: str, cfg: Dict[str, Any]) -> None:
        config = ServerConfig(
            server_id=server_id,
            command=cfg.get("command", ""),
            args=list(cfg.get("args") or []),
            env=dict(cfg.get("env") or {}),
            enabled=bool(cfg.get("enabled", True)),
            transport=ServerTransport(cfg.get("transport", "stdio")),
            timeout_seconds=float(cfg.get("timeout_seconds", 8.0)),
            auto_restart=bool(cfg.get("auto_restart", True)),
        )
        self.register(config)

    def load_from_file(self, file_path: Union[str, Path]) -> bool:
        """Load servers from a JSON configuration file if it exists."""
        path = Path(file_path)
        if not path.is_file():
            return False

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.load_from_dict(data)
            return True
        except Exception as exc:
            logger.warning("Failed to load MCP server config from %s: %exc", path, exc)
            return False

    def save_to_file(self, file_path: Union[str, Path]) -> None:
        """Persist current registry configurations to a JSON file."""
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "servers": {
                cfg.server_id: {
                    "command": cfg.command,
                    "args": cfg.args,
                    "env": cfg.env,
                    "enabled": cfg.enabled,
                    "transport": cfg.transport.value,
                    "timeout_seconds": cfg.timeout_seconds,
                    "auto_restart": cfg.auto_restart,
                }
                for cfg in self._configs.values()
            }
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
