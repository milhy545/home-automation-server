"""Constants for Perplexity AI Assistant integration."""
from typing import Final

DOMAIN: Final = "perplexity"

# Configuration
CONF_API_KEY: Final = "api_key"
CONF_MODEL: Final = "model"
CONF_TEMPERATURE: Final = "temperature"
CONF_MAX_TOKENS: Final = "max_tokens"
CONF_ENABLE_TTS: Final = "enable_tts"
CONF_TTS_ENTITY: Final = "tts_entity"

# Default values
DEFAULT_MODEL: Final = "sonar-pro"
DEFAULT_TEMPERATURE: Final = 0.7
DEFAULT_MAX_TOKENS: Final = 1000
DEFAULT_ENABLE_TTS: Final = False

# API
PERPLEXITY_API_URL: Final = "https://api.perplexity.ai/chat/completions"
TIMEOUT: Final = 30

# Models
AVAILABLE_MODELS: Final = [
    "sonar",
    "sonar-pro", 
    "sonar-reasoning",
    "sonar-deep-research"
]

# Services
SERVICE_ASK_QUESTION: Final = "ask_question"
SERVICE_SET_MODEL: Final = "set_model"

# Entities
SENSOR_LAST_RESPONSE: Final = "last_response"
SENSOR_STATUS: Final = "status"

# Attributes
ATTR_QUESTION: Final = "question"
ATTR_RESPONSE: Final = "response"
ATTR_MODEL: Final = "model"
ATTR_TIMESTAMP: Final = "timestamp"
ATTR_SOURCES: Final = "sources"
ATTR_TOKEN_COUNT: Final = "token_count"