import sys
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from unittest.mock import patch

import src.actions as actions
import src.config as config
from src.mcp_client import MCPClient, call_mcp_tool


ROOT_DIR = Path(__file__).resolve().parents[1]
SERVER_COMMAND = f'"{sys.executable}" "{ROOT_DIR / "scripts" / "mcp_project_server.py"}"'


class MCPClientTests(unittest.TestCase):
    def setUp(self):
        self.original_mcp_server_command = config.MCP_SERVER_COMMAND
        self.original_mcp_default_tool = config.MCP_DEFAULT_TOOL
        self.original_mcp_enabled = config.MCP_ENABLED
        self.addCleanup(self._restore_runtime_config)

    def _restore_runtime_config(self):
        config.MCP_SERVER_COMMAND = self.original_mcp_server_command
        config.MCP_DEFAULT_TOOL = self.original_mcp_default_tool
        config.MCP_ENABLED = self.original_mcp_enabled

    def test_list_tools_returns_bundled_server_tools(self):
        with MCPClient(SERVER_COMMAND) as client:
            tool_names = {tool.name for tool in client.list_tools()}

        self.assertIn("project_status", tool_names)
        self.assertIn("answer_project_question", tool_names)

    def test_call_tool_returns_project_status_text(self):
        result = call_mcp_tool(SERVER_COMMAND, "project_status")

        self.assertIn("Locus project status:", result)

    def test_ask_mcp_uses_default_tool_with_query_argument(self):
        config.MCP_ENABLED = True
        config.MCP_SERVER_COMMAND = SERVER_COMMAND
        config.MCP_DEFAULT_TOOL = "answer_project_question"

        result = actions.ask_mcp("where are the intents")

        self.assertIn("intents.json", result)

    def test_execute_command_logic_prefers_mcp_when_available(self):
        with patch.object(actions.config, "MCP_ENABLED", True), patch.object(
            actions.config, "MCP_SERVER_COMMAND", SERVER_COMMAND
        ), patch.object(actions.config, "MCP_DEFAULT_TOOL", "answer_project_question"):
            with redirect_stdout(StringIO()):
                result = actions.execute_command_logic("greeting", 0.55, None)

        self.assertEqual(result, ("mcp_request", None))


if __name__ == "__main__":
    unittest.main()
