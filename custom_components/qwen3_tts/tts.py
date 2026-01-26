"""Support for Qwen3 TTS speech service."""
from __future__ import annotations

import logging
from typing import Any
import asyncio

import aiohttp
import voluptuous as vol

from homeassistant.components.tts import (
    PLATFORM_SCHEMA,
    Provider,
    TextToSpeechEntity,
    TtsAudioType,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.entity_platform import AddEntitiesCallback
import homeassistant.helpers.config_validation as cv

from .const import (
    DOMAIN,
    CONF_SPEED,
    CONF_SPEAKER,
    DEFAULT_SPEED,
    SUPPORT_LANGUAGES,
    MIN_SPEED,
    MAX_SPEED,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Qwen3 TTS speech platform via config entry."""
    base_url = hass.data[DOMAIN][config_entry.entry_id]["base_url"]
    session = hass.data[DOMAIN][config_entry.entry_id]["session"]

    # Get default speed from config entry
    default_speed = config_entry.data.get(CONF_SPEED, DEFAULT_SPEED)

    async_add_entities(
        [Qwen3TTSEntity(hass, base_url, session, default_speed, config_entry)]
    )


class Qwen3TTSEntity(TextToSpeechEntity):
    """Qwen3 TTS speech API provider."""

    def __init__(
        self,
        hass: HomeAssistant,
        base_url: str,
        session: aiohttp.ClientSession,
        default_speed: float,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize Qwen3 TTS provider."""
        self.hass = hass
        self._base_url = base_url
        self._session = session
        self._default_speed = default_speed
        self._config_entry = config_entry
        self._attr_name = "Qwen3 TTS"
        self._attr_unique_id = f"{DOMAIN}_{config_entry.entry_id}"

    @property
    def default_language(self) -> str:
        """Return the default language."""
        return "zh"

    @property
    def supported_languages(self) -> list[str]:
        """Return list of supported languages."""
        return SUPPORT_LANGUAGES

    @property
    def supported_options(self) -> list[str]:
        """Return list of supported options."""
        return [CONF_SPEED, CONF_SPEAKER]

    @property
    def default_options(self) -> dict[str, Any]:
        """Return default options."""
        return {CONF_SPEED: self._default_speed}

    async def async_get_tts_audio(
        self, message: str, language: str, options: dict[str, Any]
    ) -> TtsAudioType:
        """Load TTS from Qwen3 TTS server."""
        speed = options.get(CONF_SPEED, self._default_speed)
        speaker = options.get(CONF_SPEAKER)

        # Validate speed
        if not MIN_SPEED <= speed <= MAX_SPEED:
            _LOGGER.warning(
                "Speed %.2f is out of range (%.1f-%.1f), using default %.1f",
                speed,
                MIN_SPEED,
                MAX_SPEED,
                self._default_speed,
            )
            speed = self._default_speed

        try:
            # Choose endpoint based on whether a speaker is specified
            if speaker:
                url = f"{self._base_url}/api/tts_to_speaker"
                params = {"text": message, "speaker": speaker, "speed": speed}
                _LOGGER.debug(
                    "Requesting TTS with speaker '%s': %s (speed: %.2f)",
                    speaker,
                    message[:50],
                    speed,
                )
            else:
                url = f"{self._base_url}/api/tts"
                # MLX-Audio version requires language and speaker parameters
                params = {
                    "text": message,
                    "speed": speed,
                    "language": "Chinese",
                    "speaker": "Vivian"
                }
                _LOGGER.debug(
                    "Requesting TTS: %s (speed: %.2f)", message[:50], speed
                )

            # MLX-Audio version is much faster, 10 seconds is sufficient
            async with asyncio.timeout(10):
                async with self._session.post(url, params=params) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        _LOGGER.error(
                            "TTS request failed with status %s: %s",
                            response.status,
                            error_text,
                        )
                        return None, None

                    data = await response.read()

                    if not data:
                        _LOGGER.error("Received empty audio data from TTS server")
                        return None, None

                    _LOGGER.debug(
                        "Successfully received TTS audio (%d bytes)", len(data)
                    )
                    return "wav", data

        except asyncio.TimeoutError:
            _LOGGER.error("Timeout waiting for TTS response from %s", url)
            return None, None
        except aiohttp.ClientError as err:
            _LOGGER.error("Error communicating with TTS server: %s", err)
            return None, None
        except Exception as err:
            _LOGGER.exception("Unexpected error during TTS request: %s", err)
            return None, None

    async def async_get_speakers(self) -> list[str] | None:
        """Return a list of available speakers."""
        try:
            url = f"{self._base_url}/api/list_speakers"
            async with asyncio.timeout(10):
                async with self._session.get(url) as response:
                    if response.status != 200:
                        _LOGGER.warning(
                            "Failed to get speakers list: status %s", response.status
                        )
                        return None

                    data = await response.json()
                    speakers = [s["name"] for s in data.get("speakers", [])]
                    _LOGGER.debug("Available speakers: %s", speakers)
                    return speakers if speakers else None

        except (asyncio.TimeoutError, aiohttp.ClientError) as err:
            _LOGGER.warning("Error fetching speakers list: %s", err)
            return None
