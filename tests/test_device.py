"""Tests for pfSense device registration helpers."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "custom_components"
    / "pfsense"
    / "device.py"
)
SPEC = importlib.util.spec_from_file_location("pfsense_device", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)

get_gateway_device_unique_id = MODULE.get_gateway_device_unique_id


class GetGatewayDeviceUniqueIdTests(unittest.TestCase):
    """Cover stable gateway device ID selection."""

    def test_prefers_cached_unique_id(self) -> None:
        """Keep using the cached gateway ID once it is known."""
        self.assertEqual(
            get_gateway_device_unique_id(
                "entry-device-id",
                None,
                "firewall-device-id",
            ),
            "firewall-device-id",
        )

    def test_uses_current_unique_id_when_no_cache(self) -> None:
        """Use the live pfSense ID when no cached value exists yet."""
        self.assertEqual(
            get_gateway_device_unique_id(
                "entry-device-id",
                "firewall-device-id",
            ),
            "firewall-device-id",
        )

    def test_falls_back_to_config_entry_unique_id(self) -> None:
        """Use the config entry ID if pfSense does not report one."""
        self.assertEqual(
            get_gateway_device_unique_id("entry-device-id", None),
            "entry-device-id",
        )


if __name__ == "__main__":
    unittest.main()
