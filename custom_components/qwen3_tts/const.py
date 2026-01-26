"""Constants for the Qwen3 TTS integration."""
from homeassistant.const import CONF_HOST, CONF_PORT

DOMAIN = "qwen3_tts"

# Default values
DEFAULT_HOST = "localhost"
DEFAULT_PORT = 7861  # MLX-Audio version port (7860 was Docker version)
DEFAULT_SPEED = 1.0
DEFAULT_TIMEOUT = 60  # Default base timeout in seconds

# Configuration keys
CONF_SPEED = "speed"
CONF_SPEAKER = "speaker"
CONF_TIMEOUT = "timeout"

# Supported languages (Qwen3-TTS supports 10 languages)
SUPPORT_LANGUAGES = [
    "zh",  # Chinese
    "en",  # English
    "ja",  # Japanese
    "ko",  # Korean
    "de",  # German
    "fr",  # French
    "ru",  # Russian
    "pt",  # Portuguese
    "es",  # Spanish
    "it",  # Italian
]

# Speed range
MIN_SPEED = 0.5
MAX_SPEED = 2.0

# Timeout range (in seconds)
MIN_TIMEOUT = 10
MAX_TIMEOUT = 300
