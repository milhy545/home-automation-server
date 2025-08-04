"""Sensor platform for Perplexity AI Assistant."""
import logging
from datetime import datetime
from typing import Any, Dict, Optional

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    ATTR_QUESTION,
    ATTR_RESPONSE,
    ATTR_MODEL,
    ATTR_TIMESTAMP,
    ATTR_SOURCES,
    ATTR_TOKEN_COUNT,
)

_LOGGER = logging.getLogger(__name__)

SENSORS = [
    SensorEntityDescription(
        key="last_response",
        name="Last Response",
        icon="mdi:chat-question",
    ),
    SensorEntityDescription(
        key="status", 
        name="Status",
        icon="mdi:api",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Perplexity sensors."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]
    api_client = hass.data[DOMAIN][config_entry.entry_id]["api_client"]
    
    entities = []
    for sensor_desc in SENSORS:
        entities.append(
            PerplexitySensor(
                coordinator, 
                config_entry,
                api_client,
                sensor_desc
            )
        )
    
    async_add_entities(entities)


class PerplexitySensor(CoordinatorEntity, SensorEntity):
    """Perplexity AI sensor."""

    def __init__(
        self,
        coordinator,
        config_entry: ConfigEntry,
        api_client,
        entity_description: SensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = entity_description
        self.config_entry = config_entry
        self.api_client = api_client
        
        self._attr_unique_id = f"{config_entry.entry_id}_{entity_description.key}"
        self._attr_name = f"Perplexity {entity_description.name}"
        
        # State attributes
        self._last_question: Optional[str] = None
        self._last_response: Optional[str] = None
        self._last_model: Optional[str] = None
        self._last_timestamp: Optional[str] = None
        self._sources: list = []
        self._token_count: int = 0

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""
        return DeviceInfo(
            identifiers={(DOMAIN, self.config_entry.entry_id)},
            name="Perplexity AI Assistant",
            manufacturer="Perplexity AI",
            model="API Integration",
            sw_version="1.0.0",
        )

    @property
    def native_value(self) -> str:
        """Return the state of the sensor."""
        if self.entity_description.key == "last_response":
            return self._last_response or "Ready"
        elif self.entity_description.key == "status":
            if self.coordinator.data:
                return self.coordinator.data.get("status", "unknown")
            return "unknown"
        return None

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return additional attributes."""
        attrs = {}
        
        if self.entity_description.key == "last_response":
            if self._last_question:
                attrs[ATTR_QUESTION] = self._last_question
            if self._last_model:
                attrs[ATTR_MODEL] = self._last_model
            if self._last_timestamp:
                attrs[ATTR_TIMESTAMP] = self._last_timestamp
            if self._sources:
                attrs[ATTR_SOURCES] = self._sources
            if self._token_count:
                attrs[ATTR_TOKEN_COUNT] = self._token_count
                
        elif self.entity_description.key == "status":
            if self.coordinator.data:
                attrs.update(self.coordinator.data)
            attrs["current_model"] = self.api_client.model
            attrs["temperature"] = self.api_client.temperature
            attrs["max_tokens"] = self.api_client.max_tokens
        
        return attrs

    async def async_ask_question(self, question: str, **kwargs) -> Dict[str, Any]:
        """Ask a question and update sensor state."""
        try:
            _LOGGER.debug("Asking question via sensor: %s", question[:50])
            
            response = await self.api_client.ask_question(question, **kwargs)
            
            # Update sensor state
            self._last_question = question
            self._last_response = response.get("answer", "")
            self._last_model = response.get("model", "")
            self._last_timestamp = response.get("timestamp", "")
            self._sources = response.get("sources", [])
            self._token_count = response.get("token_count", 0)
            
            # Notify HA of state change
            self.async_write_ha_state()
            
            # Fire event
            self.hass.bus.async_fire("perplexity_question_answered", {
                "entity_id": self.entity_id,
                "question": question,
                "response": response
            })
            
            return response
            
        except Exception as err:
            _LOGGER.error("Failed to ask question: %s", err)
            self._last_response = f"Error: {err}"
            self.async_write_ha_state()
            raise

    async def async_added_to_hass(self) -> None:
        """When entity is added to hass."""
        await super().async_added_to_hass()
        
        # Register service for this entity
        if self.entity_description.key == "last_response":
            
            async def ask_question_service(call):
                """Handle ask_question service for this entity."""
                question = call.data.get("question", "")
                if question:
                    await self.async_ask_question(question)
            
            # Register entity-specific service
            self.hass.services.async_register(
                DOMAIN,
                f"ask_question_{self.entity_id.split('.')[-1]}",
                ask_question_service
            )