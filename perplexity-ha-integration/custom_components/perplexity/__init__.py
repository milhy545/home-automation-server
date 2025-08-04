"""Perplexity AI Assistant integration for Home Assistant."""
import logging
from datetime import timedelta

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN, CONF_API_KEY, AVAILABLE_MODELS
from .perplexity_api import PerplexityAPIClient

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]
SCAN_INTERVAL = timedelta(seconds=30)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Perplexity AI Assistant from a config entry."""
    _LOGGER.debug("Setting up Perplexity integration for entry: %s", entry.entry_id)
    
    api_key = entry.data[CONF_API_KEY]
    
    # Create API client
    api_client = PerplexityAPIClient(api_key, hass)
    
    # Validate API connection
    try:
        await api_client.validate_connection()
    except Exception as err:
        _LOGGER.error("Failed to connect to Perplexity API: %s", err)
        return False
    
    # Create coordinator
    coordinator = PerplexityDataUpdateCoordinator(hass, api_client)
    
    # Store in hass.data
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "coordinator": coordinator,
        "api_client": api_client,
    }
    
    # Forward setup to platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    # Register services
    await _async_register_services(hass)
    
    _LOGGER.info("Perplexity AI Assistant integration setup completed")
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    _LOGGER.debug("Unloading Perplexity integration for entry: %s", entry.entry_id)
    
    # Unload platforms
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
        
        # Remove services if this is the last instance
        if not hass.data[DOMAIN]:
            hass.services.async_remove(DOMAIN, "ask_question")
            hass.services.async_remove(DOMAIN, "set_model")
    
    return unload_ok


async def _async_register_services(hass: HomeAssistant) -> None:
    """Register integration services."""
    
    async def ask_question_service(call):
        """Handle ask_question service call."""
        question = call.data.get("question")
        entity_id = call.data.get("entity_id")
        model = call.data.get("model")
        temperature = call.data.get("temperature")
        max_tokens = call.data.get("max_tokens")
        
        if not question:
            _LOGGER.error("No question provided in service call")
            return
            
        # Find the appropriate integration instance
        for entry_id, data in hass.data[DOMAIN].items():
            api_client = data["api_client"]
            try:
                # Prepare kwargs for API call
                kwargs = {}
                if model:
                    kwargs["model"] = model
                if temperature is not None:
                    kwargs["temperature"] = temperature
                if max_tokens is not None:
                    kwargs["max_tokens"] = max_tokens
                
                response = await api_client.ask_question(question, **kwargs)
                
                # Update sensor entity if specified
                if entity_id:
                    state = hass.states.get(entity_id)
                    if state:
                        attributes = dict(state.attributes)
                        attributes.update({
                            "last_question": question,
                            "last_response": response.get("answer", ""),
                            "sources": response.get("sources", []),
                            "timestamp": response.get("timestamp"),
                            "model": response.get("model", ""),
                            "token_count": response.get("token_count", 0)
                        })
                        hass.states.async_set(entity_id, response.get("answer", ""), attributes)
                
                # Fire event
                hass.bus.async_fire("perplexity_question_answered", {
                    "question": question,
                    "response": response
                })
                
                break
            except Exception as err:
                _LOGGER.error("Failed to get response from Perplexity: %s", err)
    
    async def set_model_service(call):
        """Handle set_model service call."""
        model = call.data.get("model")
        
        for entry_id, data in hass.data[DOMAIN].items():
            api_client = data["api_client"]
            api_client.set_model(model)
            break
    
    # Register services
    hass.services.async_register(
        DOMAIN, 
        "ask_question", 
        ask_question_service,
        schema=vol.Schema({
            vol.Required("question"): cv.string,
            vol.Optional("entity_id"): cv.entity_id,
            vol.Optional("model"): vol.In(AVAILABLE_MODELS),
            vol.Optional("temperature"): vol.All(vol.Coerce(float), vol.Range(min=0.0, max=2.0)),
            vol.Optional("max_tokens"): vol.All(vol.Coerce(int), vol.Range(min=10, max=4000)),
        })
    )
    
    hass.services.async_register(
        DOMAIN,
        "set_model", 
        set_model_service,
        schema=vol.Schema({
            vol.Required("model"): vol.In(AVAILABLE_MODELS),
        })
    )


class PerplexityDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Perplexity data."""

    def __init__(self, hass: HomeAssistant, api_client: PerplexityAPIClient) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=SCAN_INTERVAL,
        )
        self.api_client = api_client

    async def _async_update_data(self):
        """Update data via library."""
        try:
            return await self.api_client.get_status()
        except Exception as exception:
            _LOGGER.error("Error communicating with Perplexity API: %s", exception)
            raise exception