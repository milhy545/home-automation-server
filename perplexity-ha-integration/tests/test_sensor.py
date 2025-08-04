"""Test the Perplexity sensor platform."""
import pytest
from unittest.mock import AsyncMock, patch

from homeassistant.const import STATE_UNKNOWN
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

from custom_components.perplexity.const import DOMAIN


class TestPerplexitySensors:
    """Test Perplexity sensors."""

    async def test_sensors_created(self, hass: HomeAssistant, setup_integration):
        """Test that sensors are created."""
        config_entry = setup_integration
        
        # Check that sensors are created
        entity_registry = er.async_get(hass)
        
        # Check last_response sensor
        last_response = entity_registry.async_get("sensor.perplexity_last_response")
        assert last_response is not None
        assert last_response.domain == "sensor"
        assert last_response.platform == DOMAIN
        
        # Check status sensor  
        status = entity_registry.async_get("sensor.perplexity_status")
        assert status is not None
        assert status.domain == "sensor"
        assert status.platform == DOMAIN

    async def test_last_response_sensor_initial_state(self, hass: HomeAssistant, setup_integration):
        """Test last response sensor initial state."""
        state = hass.states.get("sensor.perplexity_last_response")
        assert state is not None
        assert state.state == "Ready"

    async def test_status_sensor_initial_state(self, hass: HomeAssistant, setup_integration):
        """Test status sensor initial state."""
        state = hass.states.get("sensor.perplexity_status")
        assert state is not None
        # Status depends on coordinator data which might be None initially
        assert state.state in ["online", "offline", "unknown"]

    async def test_sensor_attributes(self, hass: HomeAssistant, setup_integration):
        """Test sensor attributes."""
        state = hass.states.get("sensor.perplexity_last_response")
        assert state is not None
        
        # Check device info attributes
        assert state.attributes.get("friendly_name") == "Perplexity Last Response"

    async def test_status_sensor_attributes(self, hass: HomeAssistant, setup_integration):
        """Test status sensor attributes."""
        state = hass.states.get("sensor.perplexity_status")
        assert state is not None
        
        # Should have current model and settings
        attrs = state.attributes
        assert "current_model" in attrs
        assert "temperature" in attrs
        assert "max_tokens" in attrs

    async def test_device_info(self, hass: HomeAssistant, setup_integration):
        """Test device info is set correctly."""
        entity_registry = er.async_get(hass)
        
        last_response = entity_registry.async_get("sensor.perplexity_last_response")
        assert last_response is not None
        assert last_response.device_id is not None
        
        # Check that both sensors belong to the same device
        status = entity_registry.async_get("sensor.perplexity_status")
        assert status is not None
        assert status.device_id == last_response.device_id

    async def test_sensor_ask_question_method(self, hass: HomeAssistant, setup_integration, mock_api_client):
        """Test sensor ask_question method."""
        await hass.async_block_till_done()
        
        # Get the sensor entity
        entity_id = "sensor.perplexity_last_response"
        entity = None
        
        # Find the entity object
        for entity_obj in hass.data[DOMAIN][setup_integration.entry_id]["coordinator"]._listeners:
            if hasattr(entity_obj, 'entity_id') and entity_obj.entity_id == entity_id:
                entity = entity_obj
                break
        
        if entity and hasattr(entity, 'async_ask_question'):
            # Test asking a question through the sensor
            response = await entity.async_ask_question("What is AI?")
            
            # Verify API was called
            mock_api_client.ask_question.assert_called_once_with("What is AI?")
            
            # Check that sensor state was updated
            state = hass.states.get(entity_id)
            assert state.state == "Test response from Perplexity"
            assert state.attributes.get("last_question") == "What is AI?"

    async def test_sensor_updates_on_coordinator_update(self, hass: HomeAssistant, setup_integration, mock_api_client):
        """Test that sensor updates when coordinator updates."""
        await hass.async_block_till_done()
        
        # Mock coordinator data
        coordinator = hass.data[DOMAIN][setup_integration.entry_id]["coordinator"]
        coordinator.data = {
            "status": "online",
            "model": "sonar-pro",
            "last_check": "2025-07-05T20:00:00.000000"
        }
        
        # Trigger coordinator update
        await coordinator.async_refresh()
        await hass.async_block_till_done()
        
        # Check that status sensor reflects the new data
        state = hass.states.get("sensor.perplexity_status")
        assert state.state == "online"

    async def test_sensor_handles_api_error(self, hass: HomeAssistant, setup_integration, mock_api_client):
        """Test sensor handles API errors gracefully."""
        await hass.async_block_till_done()
        
        # Mock API error
        mock_api_client.ask_question = AsyncMock(side_effect=Exception("API Error"))
        
        # Get the sensor entity
        entity_id = "sensor.perplexity_last_response"
        entity = None
        
        # Find the entity object
        for entity_obj in hass.data[DOMAIN][setup_integration.entry_id]["coordinator"]._listeners:
            if hasattr(entity_obj, 'entity_id') and entity_obj.entity_id == entity_id:
                entity = entity_obj
                break
        
        if entity and hasattr(entity, 'async_ask_question'):
            # Test asking a question that causes an error
            with pytest.raises(Exception, match="API Error"):
                await entity.async_ask_question("What is AI?")
            
            # Check that sensor shows error state
            state = hass.states.get(entity_id)
            assert "Error:" in state.state

    async def test_sensor_event_firing(self, hass: HomeAssistant, setup_integration, mock_api_client):
        """Test that sensor fires events when answering questions."""
        await hass.async_block_till_done()
        
        events = []
        
        def capture_event(event):
            events.append(event)
        
        hass.bus.async_listen("perplexity_question_answered", capture_event)
        
        # Get the sensor entity
        entity_id = "sensor.perplexity_last_response"
        entity = None
        
        # Find the entity object
        for entity_obj in hass.data[DOMAIN][setup_integration.entry_id]["coordinator"]._listeners:
            if hasattr(entity_obj, 'entity_id') and entity_obj.entity_id == entity_id:
                entity = entity_obj
                break
        
        if entity and hasattr(entity, 'async_ask_question'):
            # Ask a question
            await entity.async_ask_question("Test question")
            
            # Verify event was fired
            assert len(events) == 1
            event = events[0]
            assert event.data["entity_id"] == entity_id
            assert event.data["question"] == "Test question"