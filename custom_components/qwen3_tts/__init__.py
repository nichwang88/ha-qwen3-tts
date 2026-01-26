"""Qwen3 TTS integration for Home Assistant."""
from __future__ import annotations

import logging
from typing import Any

import aiohttp
import asyncio

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.TTS]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Qwen3 TTS from a config entry."""
    host = entry.data[CONF_HOST]
    port = entry.data[CONF_PORT]

    # Verify connection to Qwen3 TTS server
    url = f"http://{host}:{port}/health"
    session = async_get_clientsession(hass)

    try:
        async with asyncio.timeout(10):
            async with session.get(url) as response:
                if response.status != 200:
                    raise ConfigEntryNotReady(
                        f"Qwen3 TTS server returned status {response.status}"
                    )
                data = await response.json()
                _LOGGER.info(
                    "Successfully connected to Qwen3 TTS server at %s:%s (status: %s)",
                    host,
                    port,
                    data.get("status"),
                )
    except asyncio.TimeoutError as err:
        raise ConfigEntryNotReady(
            f"Timeout connecting to Qwen3 TTS server at {host}:{port}"
        ) from err
    except aiohttp.ClientError as err:
        raise ConfigEntryNotReady(
            f"Error connecting to Qwen3 TTS server at {host}:{port}: {err}"
        ) from err

    # Store the base URL in hass.data
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "base_url": f"http://{host}:{port}",
        "session": session,
    }

    # Forward the setup to the TTS platform
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Register update listener to reload on config changes
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry when options are updated."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
