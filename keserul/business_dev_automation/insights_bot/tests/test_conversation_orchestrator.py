"""
Tests for the ConversationOrchestrator class.

This module contains unit tests for the ConversationOrchestrator class,
focusing on state transitions and integration with mocked LLM responses.
"""

import json
import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch

import pytest

from ..utils.conversation_orchestrator import (
    ConversationContext,
    ConversationEvent,
    ConversationOrchestrator,
    ConversationState
)
from ..utils.llm_client import LLMResponse, TokenUsage


class TestConversationContext(unittest.TestCase):
    """Tests for the ConversationContext class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.variables = {
            "company_name": "Acme Corp",
            "market_segment": "Software",
            "region": "Asia Pacific",
            "time_period": "2023-2025"
        }
        self.context = ConversationContext(self.variables)
    
    def test_initialization(self):
        """Test initialization of the context."""
        self.assertEqual(self.context.variables, self.variables)
        self.assertEqual(self.context.history, [])
        self.assertEqual(self.context.charts, [])
        self.assertEqual(self.context.current_phase, ConversationState.INITIAL)
        self.assertEqual(self.context.token_usage["total"], 0)
        self.assertEqual(self.context.cost["total"], 0.0)
    
    def test_add_message(self):
        """Test adding a message to the context."""
        self.context.add_message("user", "Hello")
        self.assertEqual(len(self.context.history), 1)
        self.assertEqual(self.context.history[0]["role"], "user")
        self.assertEqual(self.context.history[0]["content"], "Hello")
    
    def test_add_chart(self):
        """Test adding a chart to the context."""
        chart = {"title": "Market Share", "type": "pie"}
        self.context.add_chart(chart)
        self.assertEqual(len(self.context.charts), 1)
        self.assertEqual(self.context.charts[0], chart)
    
    def test_update_token_usage(self):
        """Test updating token usage statistics."""
        self.context.update_token_usage(
            ConversationState.PHASE_1,
            100,
            50
        )
        self.assertEqual(self.context.token_usage["prompt"], 100)
        self.assertEqual(self.context.token_usage["completion"], 50)
        self.assertEqual(self.context.token_usage["total"], 150)
        self.assertEqual(
            self.context.token_usage["by_phase"]["phase_1"]["total"],
            150
        )
    
    def test_update_cost(self):
        """Test updating cost statistics."""
        self.context.update_cost(ConversationState.PHASE_1, 0.5)
        self.assertEqual(self.context.cost["total"], 0.5)
        self.assertEqual(self.context.cost["by_phase"]["phase_1"], 0.5)
    
    def test_phase_timer(self):
        """Test phase timer functionality."""
        self.context.start_phase_timer(ConversationState.PHASE_1)
        duration = self.context.end_phase_timer(ConversationState.PHASE_1)
        self.assertGreaterEqual(duration, 0.0)
        self.assertIn("phase_1", self.context.phase_durations)
    
    def test_serialization(self):
        """Test serialization and deserialization."""
        self.context.add_message("user", "Hello")
        self.context.add_chart({"title": "Market Share", "type": "pie"})
        self.context.update_token_usage(ConversationState.PHASE_1, 100, 50)
        self.context.update_cost(ConversationState.PHASE_1, 0.5)
        
        # Serialize
        data = self.context.to_dict()
        
        # Deserialize
        new_context = ConversationContext.from_dict(data)
        
        # Check equality
        self.assertEqual(new_context.variables, self.context.variables)
        self.assertEqual(len(new_context.history), len(self.context.history))
        self.assertEqual(len(new_context.charts), len(self.context.charts))
        self.assertEqual(new_context.token_usage["total"], self.context.token_usage["total"])
        self.assertEqual(new_context.cost["total"], self.context.cost["total"])
    
    def test_save_and_load(self):
        """Test saving and loading the context."""
        self.context.add_message("user", "Hello")
        
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False) as temp:
            temp_path = temp.name
        
        try:
            # Save the context
            self.context.save(temp_path)
            
            # Load the context
            new_context = ConversationContext.load(temp_path)
            
            # Check equality
            self.assertEqual(new_context.variables, self.context.variables)
            self.assertEqual(len(new_context.history), len(self.context.history))
        finally:
            # Clean up
            os.unlink(temp_path)


class TestConversationOrchestrator(unittest.TestCase):
    """Tests for the ConversationOrchestrator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.prompt_manager = MagicMock()
        self.llm_client = MagicMock()
        self.orchestrator = ConversationOrchestrator(
            prompt_manager=self.prompt_manager,
            llm_client=self.llm_client,
            output_dir=tempfile.mkdtemp()
        )
        
        self.variables = {
            "company_name": "Acme Corp",
            "market_segment": "Software",
            "region": "Asia Pacific",
            "time_period": "2023-2025"
        }
    
    def test_initialization(self):
        """Test initialization of the orchestrator."""
        self.assertEqual(self.orchestrator.prompt_manager, self.prompt_manager)
        self.assertEqual(self.orchestrator.llm_client, self.llm_client)
        self.assertIsNotNone(self.orchestrator.output_dir)
    
    def test_start_conversation(self):
        """Test starting a new conversation."""
        # Mock the prompt manager
        self.prompt_manager.render_base_prompt.return_value = "Base prompt"
        
        # Start the conversation
        context = self.orchestrator.start_conversation(self.variables)
        
        # Check the context
        self.assertEqual(context.variables, self.variables)
        self.assertEqual(len(context.history), 1)
        self.assertEqual(context.history[0]["role"], "system")
        self.assertEqual(context.history[0]["content"], "Base prompt")
        self.assertEqual(context.current_phase, ConversationState.PHASE_1)
    
    def test_transition(self):
        """Test state transitions."""
        context = ConversationContext(self.variables)
        
        # Initial to Phase 1
        context.current_phase = ConversationState.INITIAL
        new_state = self.orchestrator.transition(context, ConversationEvent.START)
        self.assertEqual(new_state, ConversationState.PHASE_1)
        
        # Phase 1 to Phase 2
        context.current_phase = ConversationState.PHASE_1
        new_state = self.orchestrator.transition(context, ConversationEvent.CONTINUE)
        self.assertEqual(new_state, ConversationState.PHASE_2)
        
        # Phase 2 to Phase 3
        context.current_phase = ConversationState.PHASE_2
        new_state = self.orchestrator.transition(context, ConversationEvent.CONTINUE)
        self.assertEqual(new_state, ConversationState.PHASE_3)
        
        # Phase 3 to Phase 4
        context.current_phase = ConversationState.PHASE_3
        new_state = self.orchestrator.transition(context, ConversationEvent.CONTINUE)
        self.assertEqual(new_state, ConversationState.PHASE_4)
        
        # Phase 4 to Phase 5
        context.current_phase = ConversationState.PHASE_4
        new_state = self.orchestrator.transition(context, ConversationEvent.CONTINUE)
        self.assertEqual(new_state, ConversationState.PHASE_5)
        
        # Phase 5 to Phase 6
        context.current_phase = ConversationState.PHASE_5
        new_state = self.orchestrator.transition(context, ConversationEvent.CONTINUE)
        self.assertEqual(new_state, ConversationState.PHASE_6)
        
        # Phase 6 to Finalization
        context.current_phase = ConversationState.PHASE_6
        new_state = self.orchestrator.transition(context, ConversationEvent.FINALIZE)
        self.assertEqual(new_state, ConversationState.FINALIZATION)
        
        # Finalization to Complete
        context.current_phase = ConversationState.FINALIZATION
        new_state = self.orchestrator.transition(context, ConversationEvent.COMPLETE)
        self.assertEqual(new_state, ConversationState.COMPLETE)
    
    def test_invalid_transition(self):
        """Test invalid state transitions."""
        context = ConversationContext(self.variables)
        
        # Invalid event for state
        context.current_phase = ConversationState.PHASE_1
        with self.assertRaises(ValueError):
            self.orchestrator.transition(context, ConversationEvent.FINALIZE)
        
        # Invalid state
        context.current_phase = "invalid_state"
        with self.assertRaises(ValueError):
            self.orchestrator.transition(context, ConversationEvent.CONTINUE)
    
    def test_process_user_message_continue(self):
        """Test processing a 'continue' message."""
        # Mock the prompt manager and LLM client
        self.prompt_manager.render_phase.return_value = "Phase 2 prompt"
        
        token_usage = TokenUsage(prompt_tokens=100, completion_tokens=50)
        llm_response = LLMResponse(
            content="Phase 2 response",
            token_usage=token_usage,
            cost=0.5,
            model="gpt-4",
            provider="test",
            thinking_time=0.0
        )
        self.llm_client.query.return_value = llm_response
        
        # Create a context in Phase 1
        context = ConversationContext(self.variables)
        context.current_phase = ConversationState.PHASE_1
        
        # Process the message
        response, new_state = self.orchestrator.process_user_message(context, "continue")
        
        # Check the response and state
        self.assertEqual(response, "Phase 2 response")
        self.assertEqual(new_state, ConversationState.PHASE_2)
        
        # Check that the prompt manager was called correctly
        self.prompt_manager.render_phase.assert_called_once_with(2, self.variables)
        
        # Check that the LLM client was called correctly
        self.llm_client.query.assert_called_once()
        
        # Check that the token usage and cost were updated
        self.assertEqual(context.token_usage["total"], 150)
        self.assertEqual(context.cost["total"], 0.5)
    
    def test_process_user_message_finalize(self):
        """Test processing a 'finalize' message."""
        # Mock the prompt manager and LLM client
        self.prompt_manager.render_finalization.return_value = "Finalization prompt"
        
        token_usage = TokenUsage(prompt_tokens=100, completion_tokens=50)
        llm_response = LLMResponse(
            content="Finalization response",
            token_usage=token_usage,
            cost=0.5,
            model="gpt-4",
            provider="test",
            thinking_time=0.0
        )
        self.llm_client.query.return_value = llm_response
        
        # Create a context in Phase 6
        context = ConversationContext(self.variables)
        context.current_phase = ConversationState.PHASE_6
        
        # Process the message
        response, new_state = self.orchestrator.process_user_message(context, "finalize")
        
        # Check the response and state
        self.assertEqual(response, "Finalization response")
        self.assertEqual(new_state, ConversationState.FINALIZATION)
        
        # Check that the prompt manager was called correctly
        self.prompt_manager.render_finalization.assert_called_once_with(self.variables)
        
        # Check that the LLM client was called correctly
        self.llm_client.query.assert_called_once()
        
        # Check that the token usage and cost were updated
        self.assertEqual(context.token_usage["total"], 150)
        self.assertEqual(context.cost["total"], 0.5)
    
    def test_process_user_message_complete(self):
        """Test processing a 'complete' message."""
        # Create a context in Finalization
        context = ConversationContext(self.variables)
        context.current_phase = ConversationState.FINALIZATION
        
        # Process the message
        response, new_state = self.orchestrator.process_user_message(context, "complete")
        
        # Check the response and state
        self.assertEqual(response, "Conversation complete. The deck has been generated.")
        self.assertEqual(new_state, ConversationState.COMPLETE)
    
    def test_process_user_message_regular(self):
        """Test processing a regular message."""
        # Mock the LLM client
        token_usage = TokenUsage(prompt_tokens=100, completion_tokens=50)
        llm_response = LLMResponse(
            content="Regular response",
            token_usage=token_usage,
            cost=0.5,
            model="gpt-4",
            provider="test",
            thinking_time=0.0
        )
        self.llm_client.query.return_value = llm_response
        
        # Create a context in Phase 1
        context = ConversationContext(self.variables)
        context.current_phase = ConversationState.PHASE_1
        context.add_message("system", "System message")
        
        # Process the message
        response, new_state = self.orchestrator.process_user_message(context, "Hello")
        
        # Check the response and state
        self.assertEqual(response, "Regular response")
        self.assertEqual(new_state, ConversationState.PHASE_1)
        
        # Check that the LLM client was called correctly
        self.llm_client.query.assert_called_once()
        
        # Check that the token usage and cost were updated
        self.assertEqual(context.token_usage["total"], 150)
        self.assertEqual(context.cost["total"], 0.5)
    
    def test_extract_chart_specs(self):
        """Test extracting chart specifications from content."""
        content = """
        Here's a chart specification:
        
        ## Chart Specification
        For the Market Share chart:
        **Chart Type**: Pie
        **Data Series**:
        - Company A: [30, 25, 20]
        - Company B: [20, 25, 30]
        - Company C: [50, 50, 50]
        **X-Axis**: Years
        **Y-Axis**: Market Share (%)
        **Colors**: Primary: #0066CC, Secondary: #FF9900
        **Labels**: True
        **Legend**: True
        **Notes**: Data from industry reports
        
        This chart shows the market share of the top three companies over time.
        """
        
        context = ConversationContext(self.variables)
        self.orchestrator._extract_chart_specs(context, content)
        
        self.assertEqual(len(context.charts), 1)
        self.assertEqual(context.charts[0]["title"], "Market Share")
        self.assertEqual(context.charts[0]["type"], "Pie")
        self.assertEqual(len(context.charts[0]["data_series"]), 3)


@pytest.mark.integration
class TestConversationOrchestratorIntegration:
    """Integration tests for the ConversationOrchestrator class."""
    
    @pytest.fixture
    def setup(self):
        """Set up test fixtures."""
        # Create a temporary directory for output
        output_dir = tempfile.mkdtemp()
        
        # Create mock objects
        prompt_manager = MagicMock()
        llm_client = MagicMock()
        
        # Create the orchestrator
        orchestrator = ConversationOrchestrator(
            prompt_manager=prompt_manager,
            llm_client=llm_client,
            output_dir=output_dir
        )
        
        # Variables for the conversation
        variables = {
            "company_name": "Acme Corp",
            "market_segment": "Software",
            "region": "Asia Pacific",
            "time_period": "2023-2025"
        }
        
        return {
            "orchestrator": orchestrator,
            "prompt_manager": prompt_manager,
            "llm_client": llm_client,
            "variables": variables,
            "output_dir": output_dir
        }
    
    def test_conversation_flow(self, setup):
        """Test the full conversation flow."""
        orchestrator = setup["orchestrator"]
        prompt_manager = setup["prompt_manager"]
        llm_client = setup["llm_client"]
        variables = setup["variables"]
        
        # Mock the prompt manager
        prompt_manager.render_base_prompt.return_value = "Base prompt"
        prompt_manager.render_phase.return_value = "Phase prompt"
        prompt_manager.render_finalization.return_value = "Finalization prompt"
        
        # Mock the LLM client
        token_usage = TokenUsage(prompt_tokens=100, completion_tokens=50)
        llm_response = LLMResponse(
            content="LLM response",
            token_usage=token_usage,
            cost=0.5,
            model="gpt-4",
            provider="test",
            thinking_time=0.0
        )
        llm_client.query.return_value = llm_response
        
        # Start the conversation
        context = orchestrator.start_conversation(variables)
        
        # Phase 1 to Phase 2
        response, state = orchestrator.process_user_message(context, "continue")
        assert state == ConversationState.PHASE_2
        
        # Phase 2 to Phase 3
        response, state = orchestrator.process_user_message(context, "continue")
        assert state == ConversationState.PHASE_3
        
        # Phase 3 to Phase 4
        response, state = orchestrator.process_user_message(context, "continue")
        assert state == ConversationState.PHASE_4
        
        # Phase 4 to Phase 5
        response, state = orchestrator.process_user_message(context, "continue")
        assert state == ConversationState.PHASE_5
        
        # Phase 5 to Phase 6
        response, state = orchestrator.process_user_message(context, "continue")
        assert state == ConversationState.PHASE_6
        
        # Phase 6 to Finalization
        response, state = orchestrator.process_user_message(context, "finalize")
        assert state == ConversationState.FINALIZATION
        
        # Finalization to Complete
        response, state = orchestrator.process_user_message(context, "complete")
        assert state == ConversationState.COMPLETE
        
        # Check token usage and cost
        assert context.token_usage["total"] > 0
        assert context.cost["total"] > 0
        
        # Check that all phases have timing information
        assert len(context.phase_durations) > 0 