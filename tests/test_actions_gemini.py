import unittest
from unittest.mock import patch
from types import SimpleNamespace

import src.actions as actions


class GeminiValidationTests(unittest.TestCase):
    def test_validate_gemini_configuration_requires_key(self):
        result = actions.validate_gemini_configuration("", "gemini-flash-latest")

        self.assertFalse(result.is_valid)
        self.assertEqual(result.key_error, "This field is required.")

    def test_validate_gemini_configuration_requires_model(self):
        result = actions.validate_gemini_configuration("secret", "")

        self.assertFalse(result.is_valid)
        self.assertEqual(result.model_error, "This field is required.")

    def test_validate_gemini_configuration_returns_key_error_when_listing_models_fails(self):
        client = unittest.mock.Mock()
        client.models.list.side_effect = RuntimeError("bad key")

        with patch.object(actions.genai, "Client", return_value=client):
            result = actions.validate_gemini_configuration("secret", "gemini-flash-latest")

        self.assertFalse(result.is_valid)
        self.assertIn("bad key", result.key_error)
        client.models.get.assert_not_called()

    def test_validate_gemini_configuration_returns_model_error_when_model_lookup_fails(self):
        client = unittest.mock.Mock()
        client.models.list.return_value = iter([object()])
        client.models.get.side_effect = RuntimeError("missing model")

        with patch.object(actions.genai, "Client", return_value=client):
            result = actions.validate_gemini_configuration("secret", "gemini-flash-latest")

        self.assertFalse(result.is_valid)
        self.assertIn("missing model", result.model_error)

    def test_validate_gemini_configuration_accepts_valid_key_and_model(self):
        client = unittest.mock.Mock()
        client.models.list.return_value = iter([object()])
        client.models.get.return_value = object()

        with patch.object(actions.genai, "Client", return_value=client):
            result = actions.validate_gemini_configuration("secret", "gemini-flash-latest")

        self.assertTrue(result.is_valid)
        client.models.get.assert_called_once_with(model="gemini-flash-latest")

    def test_ask_gemini_uses_current_client_generate_content(self):
        client = unittest.mock.Mock()
        client.models.generate_content.return_value = SimpleNamespace(text=" meow ")

        with patch.object(actions, "gemini_client", client):
            answer = actions.ask_gemini("hello")

        self.assertEqual(answer, "meow")
        client.models.generate_content.assert_called_once()


if __name__ == "__main__":
    unittest.main()
