"""Common fixtures for Perplexity integration tests."""
import asyncio
from unittest.mock import AsyncMock, Mock, patch

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.perplexity.const import DOMAIN, CONF_API_KEY, CONF_MODEL, DEFAULT_MODEL


@pytest.fixture
def mock_api_client():
    """Mock Perplexity API client."""
    with patch("custom_components.perplexity.PerplexityAPIClient") as mock_client:
        client = mock_client.return_value
        client.validate_connection = AsyncMock(return_value=True)
        client.ask_question = AsyncMock(return_value={
            "answer": "Test response from Perplexity",
            "sources": ["https://example.com"],
            "model": "sonar-pro",
            "timestamp": "2025-07-05T20:00:00.000000",
            "token_count": 50
        })
        client.get_status = AsyncMock(return_value={
            "status": "online",
            "model": "sonar-pro",
            "last_check": "2025-07-05T20:00:00.000000"
        })
        client.set_model = Mock()
        client.model = DEFAULT_MODEL
        client.temperature = 0.7
        client.max_tokens = 1000
        yield client


@pytest.fixture
def mock_config_entry():
    """Create a mock config entry."""
    return MockConfigEntry(
        domain=DOMAIN,
        title="Perplexity AI Test",
        data={
            CONF_API_KEY: "test_api_key_12345",
            CONF_MODEL: DEFAULT_MODEL,
            "name": "Perplexity AI Test"
        },
        entry_id="test_entry_id",
        unique_id="test_api_key_12345"[:8]
    )


@pytest.fixture
def mock_config_entry_options():
    """Create a mock config entry with options."""
    return MockConfigEntry(
        domain=DOMAIN,
        title="Perplexity AI Test",
        data={
            CONF_API_KEY: "test_api_key_12345",
            CONF_MODEL: DEFAULT_MODEL,
            "name": "Perplexity AI Test"
        },
        options={
            "temperature": 0.8,
            "max_tokens": 2000,
            "enable_tts": True,
            "tts_entity": "tts.google_translate_say"
        },
        entry_id="test_entry_id",
        unique_id="test_api_key_12345"[:8]
    )


@pytest.fixture
async def setup_integration(hass: HomeAssistant, mock_config_entry, mock_api_client):
    """Set up the Perplexity integration."""
    mock_config_entry.add_to_hass(hass)
    
    with patch("custom_components.perplexity.PerplexityAPIClient", return_value=mock_api_client):
        assert await async_setup_component(hass, DOMAIN, {})
        await hass.async_block_till_done()
    
    return mock_config_entry