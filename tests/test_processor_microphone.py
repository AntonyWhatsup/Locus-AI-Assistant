import unittest
from unittest.mock import patch

import src.config as config
import src.processor as processor


class ProcessorMicrophoneTests(unittest.TestCase):
    def setUp(self):
        self.original_microphone_device_id = config.MICROPHONE_DEVICE_ID
        self.addCleanup(self._restore_runtime_config)

    def _restore_runtime_config(self):
        config.MICROPHONE_DEVICE_ID = self.original_microphone_device_id

    def test_resolve_microphone_device_index_returns_matching_index(self):
        # Verifies the saved microphone name resolves to the current device index.
        config.MICROPHONE_DEVICE_ID = "USB Mic"

        with patch.object(processor.sr.Microphone, "list_microphone_names", return_value=["Built-in Mic", "USB Mic"]):
            device_index = processor._resolve_microphone_device_index()

        self.assertEqual(device_index, 1)

    def test_resolve_microphone_device_index_returns_none_for_stale_device(self):
        # Verifies stale saved devices fall back to the system default microphone.
        config.MICROPHONE_DEVICE_ID = "Missing Mic"

        with patch.object(processor.sr.Microphone, "list_microphone_names", return_value=["Built-in Mic", "USB Mic"]):
            device_index = processor._resolve_microphone_device_index()

        self.assertIsNone(device_index)

    def test_open_microphone_passes_resolved_device_index(self):
        # Verifies microphone construction uses the resolved runtime device index.
        with patch.object(processor, "_resolve_microphone_device_index", return_value=1):
            with patch.object(processor.sr, "Microphone") as microphone_class:
                processor._open_microphone()

        microphone_class.assert_called_once_with(device_index=1)


if __name__ == "__main__":
    unittest.main()
