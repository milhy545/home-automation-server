"""Integration tests for Perplexity AI Assistant."""
import pytest
from unittest.mock import AsyncMock, patch

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ServiceNotFound

from custom_components.perplexity.const import DOMAIN


class TestIntegrationWorkflow:
    """Test complete integration workflows."""

    async def test_complete_question_workflow(self, hass: HomeAssistant, setup_integration, mock_api_client):
        """Test complete workflow from service call to sensor update."""
        await hass.async_block_till_done()
        
        # Set up event capture
        events = []
        def capture_event(event):
            events.append(event)
        hass.bus.async_listen("perplexity_question_answered", capture_event)
        
        # Call ask_question service
        await hass.services.async_call(
            DOMAIN,
            "ask_question",
            {
                "question": "What is the capital of Czech Republic?",
                "entity_id": "sensor.perplexity_last_response"
            },
            blocking=True
        )
        
        # Verify API was called
        mock_api_client.ask_question.assert_called_once()
        
        # Check sensor state was updated
        state = hass.states.get("sensor.perplexity_last_response")
        assert state.state == "Test response from Perplexity"
        assert state.attributes["last_question"] == "What is the capital of Czech Republic?"
        assert state.attributes["sources"] == ["https://example.com"]
        assert state.attributes["model"] == "sonar-pro"
        assert "timestamp" in state.attributes
        
        # Verify event was fired
        assert len(events) == 1
        event = events[0]
        assert event.data["question"] == "What is the capital of Czech Republic?"

    async def test_model_switching_workflow(self, hass: HomeAssistant, setup_integration, mock_api_client):
        """Test switching models and asking questions."""
        await hass.async_block_till_done()
        
        # Switch to a different model
        await hass.services.async_call(
            DOMAIN,
            "set_model",
            {"model": "sonar-reasoning"},
            blocking=True
        )
        
        # Verify model was set
        mock_api_client.set_model.assert_called_once_with("sonar-reasoning")
        
        # Ask a question with the new model
        await hass.services.async_call(
            DOMAIN,
            "ask_question",
            {"question": "Explain quantum computing"},
            blocking=True
        )
        
        # Verify question was asked
        mock_api_client.ask_question.assert_called_once()

    async def test_multiple_questions_workflow(self, hass: HomeAssistant, setup_integration, mock_api_client):
        """Test asking multiple questions in sequence."""
        await hass.async_block_till_done()
        
        questions = [
            "What is AI?",
            "How does machine learning work?",
            "What is the future of technology?"
        ]
        
        for question in questions:
            await hass.services.async_call(
                DOMAIN,
                "ask_question",
                {"question": question},
                blocking=True
            )
        
        # Verify all questions were asked
        assert mock_api_client.ask_question.call_count == len(questions)

    async def test_error_recovery_workflow(self, hass: HomeAssistant, setup_integration, mock_api_client):
        """Test error recovery in the workflow."""
        await hass.async_block_till_done()
        
        # First call succeeds
        await hass.services.async_call(
            DOMAIN,
            "ask_question",
            {"question": "First question"},
            blocking=True
        )
        
        # Second call fails
        mock_api_client.ask_question.side_effect = Exception("API Error")
        
        with pytest.raises(Exception):
            await hass.services.async_call(
                DOMAIN,
                "ask_question",
                {"question": "Second question"},
                blocking=True
            )
        
        # Reset the mock for third call
        mock_api_client.ask_question.side_effect = None
        mock_api_client.ask_question.return_value = {
            "answer": "Recovered response",
            "sources": [],
            "model": "sonar-pro",
            "timestamp": "2025-07-05T20:00:00.000000",
            "token_count": 25
        }
        
        # Third call should succeed again
        await hass.services.async_call(
            DOMAIN,
            "ask_question",
            {"question": "Third question"},
            blocking=True
        )
        
        # Verify recovery
        state = hass.states.get("sensor.perplexity_last_response")
        assert state.state == "Recovered response"

    async def test_parameter_override_workflow(self, hass: HomeAssistant, setup_integration, mock_api_client):
        """Test parameter override in service calls."""
        await hass.async_block_till_done()
        
        # Call with custom parameters
        await hass.services.async_call(
            DOMAIN,
            "ask_question",
            {
                "question": "Custom question",
                "model": "sonar-deep-research",
                "temperature": 0.9,
                "max_tokens": 2000
            },
            blocking=True
        )
        
        # Verify API was called with correct parameters
        mock_api_client.ask_question.assert_called_once_with(
            "Custom question",
            model="sonar-deep-research",
            temperature=0.9,
            max_tokens=2000
        )

    async def test_sensor_state_persistence(self, hass: HomeAssistant, setup_integration, mock_api_client):
        """Test that sensor state persists across multiple questions."""
        await hass.async_block_till_done()
        
        # Ask first question
        mock_api_client.ask_question.return_value = {
            "answer": "First answer",
            "sources": ["https://source1.com"],
            "model": "sonar-pro",
            "timestamp": "2025-07-05T20:00:00.000000",
            "token_count": 30
        }
        
        await hass.services.async_call(
            DOMAIN,
            "ask_question",
            {
                "question": "First question",
                "entity_id": "sensor.perplexity_last_response"
            },
            blocking=True
        )
        
        # Check first state
        state = hass.states.get("sensor.perplexity_last_response")
        assert state.state == "First answer"
        assert state.attributes["last_question"] == "First question"
        
        # Ask second question
        mock_api_client.ask_question.return_value = {
            "answer": "Second answer",
            "sources": ["https://source2.com"],
            "model": "sonar-pro",
            "timestamp": "2025-07-05T20:01:00.000000",
            "token_count": 40
        }
        
        await hass.services.async_call(
            DOMAIN,
            "ask_question",
            {
                "question": "Second question",
                "entity_id": "sensor.perplexity_last_response"
            },
            blocking=True
        )
        
        # Check that state was updated
        state = hass.states.get("sensor.perplexity_last_response")
        assert state.state == "Second answer"
        assert state.attributes["last_question"] == "Second question"
        assert state.attributes["sources"] == ["https://source2.com"]

    async def test_concurrent_questions(self, hass: HomeAssistant, setup_integration, mock_api_client):
        """Test handling concurrent question requests."""
        await hass.async_block_till_done()
        
        # Set up mock to track calls
        call_count = 0
        original_ask_question = mock_api_client.ask_question
        
        async def counting_ask_question(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            return await original_ask_question(*args, **kwargs)
        
        mock_api_client.ask_question = counting_ask_question
        
        # Make concurrent service calls
        import asyncio
        tasks = []
        for i in range(3):
            task = hass.services.async_call(
                DOMAIN,
                "ask_question",
                {"question": f"Question {i}"},
                blocking=True
            )
            tasks.append(task)
        
        await asyncio.gather(*tasks)
        
        # Verify all calls were made
        assert call_count == 3