"""Config flow for Qwen3 TTS integration."""
from __future__ import annotations

import logging
from typing import Any

import aiohttp
import asyncio
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    DOMAIN,
    DEFAULT_HOST,
    DEFAULT_PORT,
    DEFAULT_SPEED,
    CONF_SPEED,
    MIN_SPEED,
    MAX_SPEED,
)

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST, default=DEFAULT_HOST): str,
        vol.Required(CONF_PORT, default=DEFAULT_PORT): int,
        vol.Optional(CONF_SPEED, default=DEFAULT_SPEED): vol.All(
            vol.Coerce(float), vol.Range(min=MIN_SPEED, max=MAX_SPEED)
        ),
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """
    host = data[CONF_HOST]
    port = data[CONF_PORT]
    url = f"http://{host}:{port}/health"

    session = async_get_clientsession(hass)

    try:
        async with asyncio.timeout(10):
            async with session.get(url) as response:
                if response.status != 200:
                    raise CannotConnect(f"Server returned status {response.status}")
                result = await response.json()
                _LOGGER.debug("Health check response: %s", result)
    except asyncio.TimeoutError as err:
        raise CannotConnect("Timeout connecting to Qwen3 TTS server") from err
    except aiohttp.ClientError as err:
        raise CannotConnect(f"Error connecting to server: {err}") from err

    # Return info that you want to store in the config entry.
    return {
        "title": f"Qwen3 TTS ({host}:{port})",
        "server_status": result.get("status", "unknown"),
    }


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Qwen3 TTS."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                # Set unique ID to prevent duplicate entries
                await self.async_set_unique_id(
                    f"{user_input[CONF_HOST]}:{user_input[CONF_PORT]}"
                )
                self._abort_if_unique_id_configured()

                return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
            description_placeholders={
                "default_host": DEFAULT_HOST,
                "default_port": str(DEFAULT_PORT),
            },
        )

    async def async_step_import(self, import_data: dict[str, Any]) -> FlowResult:
        """Import a config entry from configuration.yaml."""
        return await self.async_step_user(import_data)


class CannotConnect(Exception):
    """Error to indicate we cannot connect."""
