import sys
import unittest
from pathlib import Path

from src.mcp import (
    MCPGateway,
    MCPToolNotFoundError,
    RiskLevel,
    ServerConfig,
    ServerRegistry,
    ServerStatus,
    get_gateway,
    reset_gateway,
)

ROOT_DIR = Path(__file__).resolve().parents[1]
SERVER_SCRIPT = str(ROOT_DIR / "scripts" / "mcp_project_server.py")


class MCPGatewayTests(unittest.TestCase):
    def setUp(self):
        reset_gateway()
        self.registry = ServerRegistry()
        self.server_cfg = ServerConfig(
            server_id="project",
            command=sys.executable,
            args=[SERVER_SCRIPT],
            enabled=True,
            timeout_seconds=8.0,
        )
        self.registry.register(self.server_cfg)
        self.gateway = MCPGateway(registry=self.registry)
        self.addCleanup(self.gateway.stop_all)
        self.addCleanup(reset_gateway)

    def test_registry_registration_and_filtering(self):
        self.assertEqual(len(self.registry.list_all()), 1)
        self.assertEqual(len(self.registry.list_enabled()), 1)

        disabled_cfg = ServerConfig(
            server_id="dummy",
            command="dummy_cmd",
            enabled=False,
        )
        self.registry.register(disabled_cfg)
        self.assertEqual(len(self.registry.list_all()), 2)
        self.assertEqual(len(self.registry.list_enabled()), 1)

    def test_gateway_server_lifecycle(self):
        self.assertEqual(self.gateway.get_status("project"), ServerStatus.DISCONNECTED)
        started = self.gateway.start_server("project")
        self.assertTrue(started)
        self.assertEqual(self.gateway.get_status("project"), ServerStatus.CONNECTED)

        self.gateway.stop_server("project")
        self.assertEqual(self.gateway.get_status("project"), ServerStatus.DISCONNECTED)

    def test_gateway_list_all_tools_aggregates_with_server_id(self):
        tools = self.gateway.list_all_tools()
        self.assertTrue(len(tools) >= 2)

        tool_names = {t.name for t in tools}
        self.assertIn("project_status", tool_names)
        self.assertIn("answer_project_question", tool_names)

        for tool in tools:
            self.assertEqual(tool.server_id, "project")
            self.assertTrue(tool.qualified_name.startswith("project__"))

    def test_gateway_resolve_tool(self):
        # 1. Namespaced with double underscore
        server_id, name = self.gateway.resolve_tool("project__project_status")
        self.assertEqual(server_id, "project")
        self.assertEqual(name, "project_status")

        # 2. Namespaced with colon
        server_id, name = self.gateway.resolve_tool("project:project_status")
        self.assertEqual(server_id, "project")
        self.assertEqual(name, "project_status")

        # 3. Bare tool name auto-discovery
        server_id, name = self.gateway.resolve_tool("project_status")
        self.assertEqual(server_id, "project")
        self.assertEqual(name, "project_status")

        # 4. Unknown tool raises error
        with self.assertRaises(MCPToolNotFoundError):
            self.gateway.resolve_tool("non_existent_tool_12345")

    def test_gateway_execute_tool_success(self):
        result = self.gateway.execute_tool("project__project_status")
        self.assertTrue(result.success)
        self.assertIn("Locus project status:", result.content or "")
        self.assertEqual(result.server_id, "project")

    def test_gateway_execute_tool_with_arguments(self):
        result = self.gateway.execute_tool(
            "answer_project_question",
            arguments={"query": "where are the intents stored?"},
        )
        self.assertTrue(result.success)
        self.assertIn("intents.json", result.content or "")

    def test_gateway_execute_tool_handles_missing_tool_safely(self):
        result = self.gateway.execute_tool("unknown_tool_xyz")
        self.assertFalse(result.success)
        self.assertIn("could not be resolved", result.error or "")


if __name__ == "__main__":
    unittest.main()
