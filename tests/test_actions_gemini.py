import unittest
from unittest.mock import patch

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
        with patch.object(actions.genai, "configure"), patch.object(
            actions.genai, "list_models", side_effect=RuntimeError("bad key")
        ), patch.object(actions.genai, "get_model") as get_model:
            result = actions.validate_gemini_configuration("secret", "gemini-flash-latest")

        self.assertFalse(result.is_valid)
        self.assertIn("bad key", result.key_error)
        get_model.assert_not_called()

    def test_validate_gemini_configuration_returns_model_error_when_model_lookup_fails(self):
        with patch.object(actions.genai, "configure"), patch.object(
            actions.genai, "list_models", return_value=iter([object()])
        ), patch.object(actions.genai, "get_model", side_effect=RuntimeError("missing model")):
            result = actions.validate_gemini_configuration("secret", "gemini-flash-latest")

        self.assertFalse(result.is_valid)
        self.assertIn("missing model", result.model_error)

    def test_validate_gemini_configuration_accepts_valid_key_and_model(self):
        with patch.object(actions.genai, "configure"), patch.object(
            actions.genai, "list_models", return_value=iter([object()])
        ), patch.object(actions.genai, "get_model", return_value=object()) as get_model:
            result = actions.validate_gemini_configuration("secret", "gemini-flash-latest")

        self.assertTrue(result.is_valid)
        get_model.assert_called_once_with("models/gemini-flash-latest")


if __name__ == "__main__":
    unittest.main()
