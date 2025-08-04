"""Config flow for Perplexity AI Assistant integration."""
import logging
from typing import Any, Dict, Optional

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    DOMAIN,
    CONF_API_KEY,
    CONF_MODEL,
    CONF_TEMPERATURE,
    CONF_MAX_TOKENS,
    CONF_ENABLE_TTS,
    CONF_TTS_ENTITY,
    DEFAULT_MODEL,
    DEFAULT_TEMPERATURE,
    DEFAULT_MAX_TOKENS,
    DEFAULT_ENABLE_TTS,
    AVAILABLE_MODELS,
)
from .perplexity_api import PerplexityAPIClient

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema({
    vol.Required(CONF_API_KEY): str,
    vol.Optional(CONF_MODEL, default=DEFAULT_MODEL): vol.In(AVAILABLE_MODELS),
    vol.Optional(CONF_NAME, default="Perplexity AI"): str,
})

STEP_OPTIONS_DATA_SCHEMA = vol.Schema({
    vol.Optional(CONF_TEMPERATURE, default=DEFAULT_TEMPERATURE): vol.All(
        vol.Coerce(float), vol.Range(min=0.0, max=2.0)
    ),
    vol.Optional(CONF_MAX_TOKENS, default=DEFAULT_MAX_TOKENS): vol.All(
        vol.Coerce(int), vol.Range(min=10, max=4000)
    ),
    vol.Optional(CONF_ENABLE_TTS, default=DEFAULT_ENABLE_TTS): bool,
})


async def validate_input(hass: HomeAssistant, data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate the user input allows us to connect."""
    api_key = data[CONF_API_KEY]
    
    # Test the API connection
    client = PerplexityAPIClient(api_key, hass)
    
    try:
        await client.validate_connection()
    except Exception as err:
        _LOGGER.error("Failed to validate API key: %s", err)
        raise InvalidAPIKey from err
    
    return {"title": data.get(CONF_NAME, "Perplexity AI")}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Perplexity AI Assistant."""

    VERSION = 1

    async def async_step_user(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: Dict[str, str] = {}
        
        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
                
                # Check if already configured
                await self.async_set_unique_id(user_input[CONF_API_KEY][:8])
                self._abort_if_unique_id_configured()
                
                return self.async_create_entry(title=info["title"], data=user_input)
                
            except InvalidAPIKey:
                errors["base"] = "invalid_api_key"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
            description_placeholders={
                "api_url": "https://www.perplexity.ai/settings/api"
            }
        )

    @staticmethod
    @config_entries.HANDLERS.register(DOMAIN)
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Create the options flow."""
        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Perplexity options flow."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        # Get TTS entities for selection
        tts_entities = []
        for entity_id, state in self.hass.states.async_all().items():
            if entity_id.startswith("tts."):
                tts_entities.append(entity_id)
        
        options_schema = vol.Schema({
            vol.Optional(
                CONF_TEMPERATURE,
                default=self.config_entry.options.get(CONF_TEMPERATURE, DEFAULT_TEMPERATURE)
            ): vol.All(vol.Coerce(float), vol.Range(min=0.0, max=2.0)),
            vol.Optional(
                CONF_MAX_TOKENS,
                default=self.config_entry.options.get(CONF_MAX_TOKENS, DEFAULT_MAX_TOKENS)
            ): vol.All(vol.Coerce(int), vol.Range(min=10, max=4000)),
            vol.Optional(
                CONF_ENABLE_TTS,
                default=self.config_entry.options.get(CONF_ENABLE_TTS, DEFAULT_ENABLE_TTS)
            ): bool,
        })
        
        if tts_entities:
            options_schema = options_schema.extend({
                vol.Optional(
                    CONF_TTS_ENTITY,
                    default=self.config_entry.options.get(CONF_TTS_ENTITY, "")
                ): vol.In([""] + tts_entities),
            })

        return self.async_show_form(
            step_id="init",
            data_schema=options_schema,
        )


class InvalidAPIKey(Exception):
    """Error to indicate invalid API key."""