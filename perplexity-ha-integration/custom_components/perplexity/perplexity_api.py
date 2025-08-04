"""Perplexity API client."""
import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, Optional

import aiohttp
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    PERPLEXITY_API_URL,
    TIMEOUT,
    DEFAULT_MODEL,
    DEFAULT_TEMPERATURE,
    DEFAULT_MAX_TOKENS,
)

_LOGGER = logging.getLogger(__name__)


class PerplexityAPIClient:
    """Client for Perplexity AI API."""

    def __init__(self, api_key: str, hass: HomeAssistant) -> None:
        """Initialize the API client."""
        self.api_key = api_key
        self.hass = hass
        self.session = async_get_clientsession(hass)
        self.model = DEFAULT_MODEL
        self.temperature = DEFAULT_TEMPERATURE
        self.max_tokens = DEFAULT_MAX_TOKENS
        
    def set_model(self, model: str) -> None:
        """Set the model to use for requests."""
        self.model = model
        _LOGGER.debug("Model set to: %s", model)
        
    def set_temperature(self, temperature: float) -> None:
        """Set the temperature for requests."""
        self.temperature = temperature
        
    def set_max_tokens(self, max_tokens: int) -> None:
        """Set the max tokens for requests."""
        self.max_tokens = max_tokens

    async def validate_connection(self) -> bool:
        """Validate the API connection."""
        try:
            response = await self._make_request("test connection", max_tokens=10)
            return True
        except Exception as err:
            _LOGGER.error("Connection validation failed: %s", err)
            raise

    async def ask_question(self, question: str, **kwargs) -> Dict[str, Any]:
        """Ask a question to Perplexity."""
        try:
            _LOGGER.debug("Asking question: %s", question[:100])
            
            # Override parameters if provided
            model = kwargs.get("model", self.model)
            temperature = kwargs.get("temperature", self.temperature)
            max_tokens = kwargs.get("max_tokens", self.max_tokens)
            
            response = await self._make_request(
                question, 
                model=model,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            return {
                "answer": response.get("answer", ""),
                "sources": response.get("sources", []),
                "model": model,
                "timestamp": datetime.now().isoformat(),
                "token_count": response.get("usage", {}).get("total_tokens", 0)
            }
            
        except Exception as err:
            _LOGGER.error("Failed to ask question: %s", err)
            raise

    async def get_status(self) -> Dict[str, Any]:
        """Get API status."""
        try:
            # Simple status check with minimal request
            await self.validate_connection()
            return {
                "status": "online",
                "model": self.model,
                "last_check": datetime.now().isoformat()
            }
        except Exception:
            return {
                "status": "offline", 
                "model": self.model,
                "last_check": datetime.now().isoformat()
            }

    async def _make_request(
        self, 
        question: str, 
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """Make request to Perplexity API."""
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model or self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "Odpovídej v češtině, buď stručný a přesný. Zahrň relevantní zdroje."
                },
                {
                    "role": "user", 
                    "content": question
                }
            ],
            "temperature": temperature or self.temperature,
            "max_tokens": max_tokens or self.max_tokens,
            "stream": False
        }
        
        try:
            timeout = aiohttp.ClientTimeout(total=TIMEOUT)
            async with self.session.post(
                PERPLEXITY_API_URL,
                headers=headers,
                json=payload,
                timeout=timeout
            ) as response:
                
                if response.status == 401:
                    raise Exception("Invalid API key")
                elif response.status == 429:
                    raise Exception("Rate limit exceeded")
                elif response.status != 200:
                    text = await response.text()
                    raise Exception(f"API error {response.status}: {text}")
                
                data = await response.json()
                
                # Extract answer from response
                answer = ""
                sources = []
                
                if "choices" in data and data["choices"]:
                    choice = data["choices"][0]
                    if "message" in choice:
                        answer = choice["message"].get("content", "")
                
                # Try to extract sources if available
                if "citations" in data:
                    sources = [cite.get("url", "") for cite in data["citations"]]
                
                return {
                    "answer": answer,
                    "sources": sources,
                    "usage": data.get("usage", {}),
                    "raw_response": data
                }
                
        except asyncio.TimeoutError:
            raise Exception("Request timeout")
        except aiohttp.ClientError as err:
            raise Exception(f"Network error: {err}")
        except Exception as err:
            _LOGGER.error("API request failed: %s", err)
            raise