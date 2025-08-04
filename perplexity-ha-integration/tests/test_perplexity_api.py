"""Test the Perplexity API client."""
import asyncio
import aiohttp
import pytest
from unittest.mock import AsyncMock, Mock, patch

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from custom_components.perplexity.perplexity_api import PerplexityAPIClient
from custom_components.perplexity.const import DEFAULT_MODEL, DEFAULT_TEMPERATURE, DEFAULT_MAX_TOKENS


class TestPerplexityAPIClient:
    """Test the Perplexity API client."""

    def setup_method(self):
        """Set up test method."""
        self.api_key = "test_api_key_12345"

    async def test_client_initialization(self, hass: HomeAssistant):
        """Test client initialization."""
        client = PerplexityAPIClient(self.api_key, hass)
        
        assert client.api_key == self.api_key
        assert client.hass == hass
        assert client.model == DEFAULT_MODEL
        assert client.temperature == DEFAULT_TEMPERATURE
        assert client.max_tokens == DEFAULT_MAX_TOKENS

    async def test_set_model(self, hass: HomeAssistant):
        """Test setting model."""
        client = PerplexityAPIClient(self.api_key, hass)
        
        client.set_model("sonar-pro")
        assert client.model == "sonar-pro"

    async def test_set_temperature(self, hass: HomeAssistant):
        """Test setting temperature."""
        client = PerplexityAPIClient(self.api_key, hass)
        
        client.set_temperature(0.8)
        assert client.temperature == 0.8

    async def test_set_max_tokens(self, hass: HomeAssistant):
        """Test setting max tokens."""
        client = PerplexityAPIClient(self.api_key, hass)
        
        client.set_max_tokens(2000)
        assert client.max_tokens == 2000

    async def test_validate_connection_success(self, hass: HomeAssistant):
        """Test successful connection validation."""
        client = PerplexityAPIClient(self.api_key, hass)
        
        # Mock successful API response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={
            "choices": [{"message": {"content": "test"}}],
            "usage": {"total_tokens": 10}
        })
        
        with patch.object(client.session, 'post', return_value=mock_response) as mock_post:
            mock_post.return_value.__aenter__.return_value = mock_response
            
            result = await client.validate_connection()
            assert result is True

    async def test_validate_connection_failure(self, hass: HomeAssistant):
        """Test connection validation failure."""
        client = PerplexityAPIClient(self.api_key, hass)
        
        # Mock failed API response
        mock_response = AsyncMock()
        mock_response.status = 401
        mock_response.text = AsyncMock(return_value="Unauthorized")
        
        with patch.object(client.session, 'post', return_value=mock_response) as mock_post:
            mock_post.return_value.__aenter__.return_value = mock_response
            
            with pytest.raises(Exception, match="Invalid API key"):
                await client.validate_connection()

    async def test_ask_question_success(self, hass: HomeAssistant):
        """Test successful question asking."""
        client = PerplexityAPIClient(self.api_key, hass)
        
        # Mock successful API response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={
            "choices": [{"message": {"content": "This is the answer"}}],
            "usage": {"total_tokens": 45},
            "citations": [{"url": "https://example.com"}]
        })
        
        with patch.object(client.session, 'post', return_value=mock_response) as mock_post:
            mock_post.return_value.__aenter__.return_value = mock_response
            
            result = await client.ask_question("What is AI?")
            
            assert result["answer"] == "This is the answer"
            assert result["sources"] == ["https://example.com"]
            assert result["model"] == DEFAULT_MODEL
            assert result["token_count"] == 45
            assert "timestamp" in result

    async def test_ask_question_with_parameters(self, hass: HomeAssistant):
        """Test asking question with custom parameters."""
        client = PerplexityAPIClient(self.api_key, hass)
        
        # Mock successful API response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={
            "choices": [{"message": {"content": "Custom response"}}],
            "usage": {"total_tokens": 30}
        })
        
        with patch.object(client.session, 'post', return_value=mock_response) as mock_post:
            mock_post.return_value.__aenter__.return_value = mock_response
            
            result = await client.ask_question(
                "Test question",
                model="sonar-pro",
                temperature=0.9,
                max_tokens=500
            )
            
            # Check that API was called with correct parameters
            call_args = mock_post.call_args
            payload = call_args[1]["json"]
            
            assert payload["model"] == "sonar-pro"
            assert payload["temperature"] == 0.9
            assert payload["max_tokens"] == 500
            assert result["answer"] == "Custom response"

    async def test_ask_question_rate_limit(self, hass: HomeAssistant):
        """Test handling rate limit error."""
        client = PerplexityAPIClient(self.api_key, hass)
        
        # Mock rate limit response
        mock_response = AsyncMock()
        mock_response.status = 429
        mock_response.text = AsyncMock(return_value="Rate limit exceeded")
        
        with patch.object(client.session, 'post', return_value=mock_response) as mock_post:
            mock_post.return_value.__aenter__.return_value = mock_response
            
            with pytest.raises(Exception, match="Rate limit exceeded"):
                await client.ask_question("Test question")

    async def test_ask_question_network_error(self, hass: HomeAssistant):
        """Test handling network error."""
        client = PerplexityAPIClient(self.api_key, hass)
        
        with patch.object(client.session, 'post', side_effect=aiohttp.ClientError("Network error")):
            with pytest.raises(Exception, match="Network error"):
                await client.ask_question("Test question")

    async def test_ask_question_timeout(self, hass: HomeAssistant):
        """Test handling timeout error."""
        client = PerplexityAPIClient(self.api_key, hass)
        
        with patch.object(client.session, 'post', side_effect=asyncio.TimeoutError()):
            with pytest.raises(Exception, match="Request timeout"):
                await client.ask_question("Test question")

    async def test_get_status_online(self, hass: HomeAssistant):
        """Test getting status when API is online."""
        client = PerplexityAPIClient(self.api_key, hass)
        
        # Mock successful validation
        with patch.object(client, 'validate_connection', return_value=True):
            result = await client.get_status()
            
            assert result["status"] == "online"
            assert result["model"] == DEFAULT_MODEL
            assert "last_check" in result

    async def test_get_status_offline(self, hass: HomeAssistant):
        """Test getting status when API is offline."""
        client = PerplexityAPIClient(self.api_key, hass)
        
        # Mock failed validation
        with patch.object(client, 'validate_connection', side_effect=Exception("API Error")):
            result = await client.get_status()
            
            assert result["status"] == "offline"
            assert result["model"] == DEFAULT_MODEL
            assert "last_check" in result

    async def test_make_request_invalid_response(self, hass: HomeAssistant):
        """Test handling invalid JSON response."""
        client = PerplexityAPIClient(self.api_key, hass)
        
        # Mock invalid JSON response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(side_effect=ValueError("Invalid JSON"))
        
        with patch.object(client.session, 'post', return_value=mock_response) as mock_post:
            mock_post.return_value.__aenter__.return_value = mock_response
            
            with pytest.raises(Exception):
                await client.ask_question("Test question")

    async def test_make_request_empty_response(self, hass: HomeAssistant):
        """Test handling empty response."""
        client = PerplexityAPIClient(self.api_key, hass)
        
        # Mock empty response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={})
        
        with patch.object(client.session, 'post', return_value=mock_response) as mock_post:
            mock_post.return_value.__aenter__.return_value = mock_response
            
            result = await client.ask_question("Test question")
            
            assert result["answer"] == ""
            assert result["sources"] == []
            assert result["token_count"] == 0