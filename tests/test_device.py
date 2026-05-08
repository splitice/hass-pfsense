"""Tests for pfSense device registration helpers."""

from __future__ import annotations

from dataclasses import dataclass, field
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
get_removable_duplicate_gateway_device_ids = (
    MODULE.get_removable_duplicate_gateway_device_ids
)


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


@dataclass
class MockDevice:
    """Minimal device-registry entry for helper tests."""

    id: str
    identifiers: set[tuple[str, str]]
    config_entries: set[str] = field(default_factory=set)
    via_device_id: str | None = None


class GetRemovableDuplicateGatewayDeviceIdsTests(unittest.TestCase):
    """Cover duplicate gateway cleanup selection."""

    def test_returns_orphaned_duplicate_gateway(self) -> None:
        """Remove older gateway devices once nothing references them."""
        devices = [
            MockDevice(
                id="canonical",
                identifiers={("pfsense", "gateway-id")},
                config_entries={"entry-id"},
            ),
            MockDevice(
                id="duplicate",
                identifiers={("pfsense", "legacy-id")},
                config_entries={"entry-id"},
            ),
        ]

        self.assertEqual(
            get_removable_duplicate_gateway_device_ids(
                devices,
                "entry-id",
                "pfsense",
                "gateway-id",
                {"canonical"},
            ),
            ["duplicate"],
        )

    def test_skips_duplicate_gateway_with_entities(self) -> None:
        """Keep duplicates that still own entity-registry entries."""
        devices = [
            MockDevice(
                id="canonical",
                identifiers={("pfsense", "gateway-id")},
                config_entries={"entry-id"},
            ),
            MockDevice(
                id="duplicate",
                identifiers={("pfsense", "legacy-id")},
                config_entries={"entry-id"},
            ),
        ]

        self.assertEqual(
            get_removable_duplicate_gateway_device_ids(
                devices,
                "entry-id",
                "pfsense",
                "gateway-id",
                {"canonical", "duplicate"},
            ),
            [],
        )

    def test_skips_duplicate_gateway_with_child_devices(self) -> None:
        """Keep duplicates while other devices still point at them."""
        devices = [
            MockDevice(
                id="canonical",
                identifiers={("pfsense", "gateway-id")},
                config_entries={"entry-id"},
            ),
            MockDevice(
                id="duplicate",
                identifiers={("pfsense", "legacy-id")},
                config_entries={"entry-id"},
            ),
            MockDevice(
                id="tracker",
                identifiers=set(),
                config_entries={"entry-id"},
                via_device_id="duplicate",
            ),
        ]

        self.assertEqual(
            get_removable_duplicate_gateway_device_ids(
                devices,
                "entry-id",
                "pfsense",
                "gateway-id",
                {"canonical", "tracker"},
            ),
            [],
        )


if __name__ == "__main__":
    unittest.main()
