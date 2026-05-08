"""Helpers for pfSense device registration."""

from __future__ import annotations

from collections.abc import Iterable

def get_gateway_device_unique_id(
    config_entry_unique_id: str | None,
    current_unique_id: str | None,
    cached_unique_id: str | None = None,
) -> str | None:
    """Return the stable unique ID to use for the pfSense gateway device."""
    if cached_unique_id:
        return cached_unique_id
    if current_unique_id:
        return current_unique_id
    return config_entry_unique_id


def get_removable_duplicate_gateway_device_ids(
    devices: Iterable,
    config_entry_id: str,
    domain: str,
    gateway_device_unique_id: str | None,
    entity_device_ids: set[str],
) -> list[str]:
    """Return duplicate gateway device IDs that can be safely removed."""
    if not gateway_device_unique_id:
        return []

    gateway_identifier = (domain, gateway_device_unique_id)
    devices = list(devices)
    duplicate_device_ids = []

    for device in devices:
        if gateway_identifier in device.identifiers:
            continue
        if not any(identifier[0] == domain for identifier in device.identifiers):
            continue
        if device.id in entity_device_ids:
            continue
        if any(other_device.via_device_id == device.id for other_device in devices):
            continue
        if device.config_entries != {config_entry_id}:
            continue
        duplicate_device_ids.append(device.id)

    return duplicate_device_ids
