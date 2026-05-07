"""Helpers for pfSense device registration."""

from __future__ import annotations


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
