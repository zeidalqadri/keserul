import pytest
from unittest.mock import patch, MagicMock
from business_dev_automation.prompt_optimizer_bot.utils.optimize_prompt import optimize_prompt
from business_dev_automation.prompt_optimizer_bot.utils.state import AgentState
from langchain_core.outputs import LLMResult

def test_optimize_prompt_success():
    with patch('prompt_optimizer_bot.utils.metagpt_agents.llm.invoke') as mock_invoke, \
         patch('prompt_optimizer_bot.utils.optimizer_orchestrator.executor_llm.invoke') as mock_executor:
        # Mock responses for initial prompt generation
        mock_invoke.side_effect = [
            LLMResult(generations=[[MagicMock(content='Initial system prompt')]], llm_output={}, run=[]),
            LLMResult(generations=[[MagicMock(content='Initial output')]], llm_output={}, run=[]),
            LLMResult(generations=[[MagicMock(content='Preferred Output ID: A')]], llm_output={}, run=[]),
            LLMResult(generations=[[MagicMock(content="Accept: Yes")]], llm_output={}, run=[])
        ]
        mock_executor.side_effect = [
            LLMResult(generations=[[MagicMock(content='Initial output')]], llm_output={}, run=[])
        ]

        result = optimize_prompt('Test user message', 'Expected output', max_iterations=1)
        assert result == 'Initial system prompt'

def test_optimize_prompt_failure():
    with patch('prompt_optimizer_bot.utils.metagpt_agents.llm.invoke') as mock_invoke, \
         patch('prompt_optimizer_bot.utils.optimizer_orchestrator.executor_llm.invoke') as mock_executor:
        mock_invoke.side_effect = [
            LLMResult(generations=[[MagicMock(content='Initial system prompt')]], llm_output={}, run=[]),
            LLMResult(generations=[[MagicMock(content='Initial output')]], llm_output={}, run=[]),
            LLMResult(generations=[[MagicMock(content='Preferred Output ID: A')]], llm_output={}, run=[]),
            LLMResult(generations=[[MagicMock(content="Accept: No")]], llm_output={}, run=[]),
            LLMResult(generations=[[MagicMock(content='Suggestions')]], llm_output={}, run=[])
        ]
        mock_executor.side_effect = [
            LLMResult(generations=[[MagicMock(content='Initial output')]], llm_output={}, run=[])
        ]

        result = optimize_prompt('Test user message', 'Expected output', max_iterations=1)
        assert result == 'Initial system prompt'  # Returns last system message if not accepted 