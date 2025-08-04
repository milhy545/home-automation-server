"""Test the Perplexity config flow."""
import pytest
from unittest.mock import AsyncMock, patch

from homeassistant import config_entries, data_entry_flow
from homeassistant.core import HomeAssistant

from custom_components.perplexity.config_flow import InvalidAPIKey
from custom_components.perplexity.const import DOMAIN, CONF_API_KEY, CONF_MODEL, DEFAULT_MODEL


class TestConfigFlow:
    """Test the config flow."""

    async def test_form(self, hass: HomeAssistant):
        """Test we get the form."""
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )
        assert result["type"] == data_entry_flow.RESULT_TYPE_FORM
        assert result["errors"] == {}

    async def test_form_valid_api_key(self, hass: HomeAssistant):
        """Test form with valid API key."""
        with patch(
            "custom_components.perplexity.config_flow.validate_input",
            return_value={"title": "Perplexity AI"}
        ):
            result = await hass.config_entries.flow.async_init(
                DOMAIN, context={"source": config_entries.SOURCE_USER}
            )

            result2 = await hass.config_entries.flow.async_configure(
                result["flow_id"],
                {
                    CONF_API_KEY: "test_api_key_12345",
                    CONF_MODEL: DEFAULT_MODEL,
                    "name": "Perplexity AI"
                },
            )
            await hass.async_block_till_done()

            assert result2["type"] == data_entry_flow.RESULT_TYPE_CREATE_ENTRY
            assert result2["title"] == "Perplexity AI"
            assert result2["data"] == {
                CONF_API_KEY: "test_api_key_12345",
                CONF_MODEL: DEFAULT_MODEL,
                "name": "Perplexity AI"
            }

    async def test_form_invalid_api_key(self, hass: HomeAssistant):
        """Test form with invalid API key."""
        with patch(
            "custom_components.perplexity.config_flow.validate_input",
            side_effect=InvalidAPIKey
        ):
            result = await hass.config_entries.flow.async_init(
                DOMAIN, context={"source": config_entries.SOURCE_USER}
            )

            result2 = await hass.config_entries.flow.async_configure(
                result["flow_id"],
                {
                    CONF_API_KEY: "invalid_key",
                    CONF_MODEL: DEFAULT_MODEL,
                    "name": "Perplexity AI"
                },
            )

            assert result2["type"] == data_entry_flow.RESULT_TYPE_FORM
            assert result2["errors"] == {"base": "invalid_api_key"}

    async def test_form_cannot_connect(self, hass: HomeAssistant):
        """Test form when we cannot connect."""
        with patch(
            "custom_components.perplexity.config_flow.validate_input",
            side_effect=Exception
        ):
            result = await hass.config_entries.flow.async_init(
                DOMAIN, context={"source": config_entries.SOURCE_USER}
            )

            result2 = await hass.config_entries.flow.async_configure(
                result["flow_id"],
                {
                    CONF_API_KEY: "test_api_key_12345",
                    CONF_MODEL: DEFAULT_MODEL,
                    "name": "Perplexity AI"
                },
            )

            assert result2["type"] == data_entry_flow.RESULT_TYPE_FORM
            assert result2["errors"] == {"base": "unknown"}

    async def test_form_already_configured(self, hass: HomeAssistant, mock_config_entry):
        """Test form when already configured."""
        mock_config_entry.add_to_hass(hass)

        with patch(
            "custom_components.perplexity.config_flow.validate_input",
            return_value={"title": "Perplexity AI"}
        ):
            result = await hass.config_entries.flow.async_init(
                DOMAIN, context={"source": config_entries.SOURCE_USER}
            )

            result2 = await hass.config_entries.flow.async_configure(
                result["flow_id"],
                {
                    CONF_API_KEY: "test_api_key_12345",
                    CONF_MODEL: DEFAULT_MODEL,
                    "name": "Perplexity AI"
                },
            )

            assert result2["type"] == data_entry_flow.RESULT_TYPE_ABORT
            assert result2["reason"] == "already_configured"


class TestOptionsFlow:
    """Test the options flow."""

    async def test_options_flow(self, hass: HomeAssistant, mock_config_entry):
        """Test options flow."""
        mock_config_entry.add_to_hass(hass)

        result = await hass.config_entries.options.async_init(mock_config_entry.entry_id)

        assert result["type"] == data_entry_flow.RESULT_TYPE_FORM
        assert result["step_id"] == "init"

        result2 = await hass.config_entries.options.async_configure(
            result["flow_id"],
            user_input={
                "temperature": 0.8,
                "max_tokens": 2000,
                "enable_tts": True
            },
        )

        assert result2["type"] == data_entry_flow.RESULT_TYPE_CREATE_ENTRY
        assert result2["data"]["temperature"] == 0.8
        assert result2["data"]["max_tokens"] == 2000
        assert result2["data"]["enable_tts"] is True