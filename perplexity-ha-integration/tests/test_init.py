"""Test the Perplexity integration initialization."""
import pytest
from unittest.mock import AsyncMock, patch

from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from custom_components.perplexity.const import DOMAIN


class TestIntegrationSetup:
    """Test integration setup."""

    async def test_setup_entry_success(self, hass: HomeAssistant, setup_integration):
        """Test successful setup of entry."""
        config_entry = setup_integration
        
        assert config_entry.state == ConfigEntryState.LOADED
        assert DOMAIN in hass.data
        assert config_entry.entry_id in hass.data[DOMAIN]
        
        # Check that coordinator and API client are set up
        data = hass.data[DOMAIN][config_entry.entry_id]
        assert "coordinator" in data
        assert "api_client" in data

    async def test_setup_entry_api_failure(self, hass: HomeAssistant, mock_config_entry):
        """Test setup failure when API validation fails."""
        mock_config_entry.add_to_hass(hass)
        
        with patch("custom_components.perplexity.PerplexityAPIClient") as mock_client:
            mock_client.return_value.validate_connection = AsyncMock(
                side_effect=Exception("API Error")
            )
            
            await hass.config_entries.async_setup(mock_config_entry.entry_id)
            await hass.async_block_till_done()
            
            assert mock_config_entry.state == ConfigEntryState.SETUP_ERROR

    async def test_unload_entry(self, hass: HomeAssistant, setup_integration):
        """Test unloading an entry."""
        config_entry = setup_integration
        
        assert config_entry.state == ConfigEntryState.LOADED
        assert DOMAIN in hass.data
        
        # Unload the entry
        assert await hass.config_entries.async_unload(config_entry.entry_id)
        assert config_entry.state == ConfigEntryState.NOT_LOADED
        
        # Data should be cleaned up
        assert config_entry.entry_id not in hass.data[DOMAIN]


class TestServices:
    """Test integration services."""

    async def test_ask_question_service(self, hass: HomeAssistant, setup_integration, mock_api_client):
        """Test ask_question service."""
        await hass.async_block_till_done()
        
        # Call the service
        await hass.services.async_call(
            DOMAIN,
            "ask_question",
            {"question": "What is the weather today?"},
            blocking=True
        )
        
        # Verify API client was called
        mock_api_client.ask_question.assert_called_once_with(
            "What is the weather today?"
        )

    async def test_ask_question_service_with_params(self, hass: HomeAssistant, setup_integration, mock_api_client):
        """Test ask_question service with parameters."""
        await hass.async_block_till_done()
        
        # Call the service with parameters
        await hass.services.async_call(
            DOMAIN,
            "ask_question",
            {
                "question": "What is AI?",
                "model": "sonar-reasoning",
                "temperature": 0.9,
                "max_tokens": 500
            },
            blocking=True
        )
        
        # Verify API client was called with correct parameters
        mock_api_client.ask_question.assert_called_once_with(
            "What is AI?",
            model="sonar-reasoning",
            temperature=0.9,
            max_tokens=500
        )

    async def test_set_model_service(self, hass: HomeAssistant, setup_integration, mock_api_client):
        """Test set_model service."""
        await hass.async_block_till_done()
        
        # Call the service
        await hass.services.async_call(
            DOMAIN,
            "set_model",
            {"model": "sonar-pro"},
            blocking=True
        )
        
        # Verify API client was called
        mock_api_client.set_model.assert_called_once_with("sonar-pro")

    async def test_ask_question_service_empty_question(self, hass: HomeAssistant, setup_integration, mock_api_client):
        """Test ask_question service with empty question."""
        await hass.async_block_till_done()
        
        # Call the service with empty question
        await hass.services.async_call(
            DOMAIN,
            "ask_question",
            {"question": ""},
            blocking=True
        )
        
        # Verify API client was not called
        mock_api_client.ask_question.assert_not_called()

    async def test_ask_question_service_with_entity_id(self, hass: HomeAssistant, setup_integration, mock_api_client):
        """Test ask_question service with entity_id parameter."""
        await hass.async_block_till_done()
        
        # Create a dummy sensor entity
        hass.states.async_set("sensor.test_sensor", "initial", {})
        
        # Call the service with entity_id
        await hass.services.async_call(
            DOMAIN,
            "ask_question",
            {
                "question": "Test question",
                "entity_id": "sensor.test_sensor"
            },
            blocking=True
        )
        
        # Verify API client was called
        mock_api_client.ask_question.assert_called_once()
        
        # Check that entity state was updated
        state = hass.states.get("sensor.test_sensor")
        assert state.state == "Test response from Perplexity"
        assert state.attributes["last_question"] == "Test question"

    async def test_event_fired_on_question(self, hass: HomeAssistant, setup_integration, mock_api_client):
        """Test that event is fired when question is answered."""
        await hass.async_block_till_done()
        
        events = []
        
        def capture_event(event):
            events.append(event)
        
        hass.bus.async_listen("perplexity_question_answered", capture_event)
        
        # Call the service
        await hass.services.async_call(
            DOMAIN,
            "ask_question",
            {"question": "Test question"},
            blocking=True
        )
        
        # Verify event was fired
        assert len(events) == 1
        event = events[0]
        assert event.data["question"] == "Test question"
        assert "response" in event.data