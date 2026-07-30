import unittest
from contextlib import redirect_stdout
from io import StringIO
from unittest.mock import patch

from src.actions import execute_command_logic


class ActionRoutingTests(unittest.TestCase):
    def test_general_gemini_fallback_is_disabled_by_default(self):
        with patch("src.actions.config.GEMINI_FALLBACK_ENABLED", False):
            result = self._execute("greeting", 0.5, None)

        self.assertEqual(result, ("unknown", None))

    def test_general_gemini_fallback_can_be_enabled(self):
        with patch("src.actions.config.GEMINI_FALLBACK_ENABLED", True):
            result = self._execute("greeting", 0.5, None)

        self.assertEqual(result, ("gemini_request", None))

    def test_unknown_profile_keeps_profile_context(self):
        result = self._execute("greeting", 0.99, "waiting_for_profile_browser")

        self.assertEqual(result, ("think", "waiting_for_profile_browser"))

    def _execute(self, tag, confidence, active_context):
        with redirect_stdout(StringIO()):
            return execute_command_logic(tag, confidence, active_context)


if __name__ == "__main__":
    unittest.main()
