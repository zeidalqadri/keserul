from metagpt.roles import Role
from metagpt.actions import Action
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from metagpt.logs import logger
from .state import AgentState
import sys
from pathlib import Path
from typing import Optional
sys.path.append(str(Path(__file__).parent.parent.parent.parent / 'archive' / 'devin.cursorrules' / 'tools'))
from token_tracker import get_token_tracker, TokenUsage, APIResponse, TokenTracker

# Import cost tracking
sys.path.append(str(Path(__file__).parent.parent.parent))
try:
    from shared.cost_manager import get_cost_manager, track_api_cost, track_metagpt_event
    COST_MANAGER_AVAILABLE = True
except ImportError:
    COST_MANAGER_AVAILABLE = False

from .cost_instrumented_wrapper import instrument_agent_action

llm = ChatOpenAI(model_name='gpt-4o', temperature=0.5)

class PromptEngineer(Role):
    def __init__(self, name='PromptEngineer'):
        super().__init__(name=name)

    @instrument_agent_action('prompt_engineer')
    async def act(self, state: AgentState) -> AgentState:
        if not state.system_message:
            initial_prompt = ChatPromptTemplate.from_messages([
                ("system", "You are a world-class prompt engineer. Your goal is to create a system prompt that, when used with the user's message, will produce the expected output."),
                ("user", "User message: {user_message}\nExpected output: {expected_output}\n\nCreate the system prompt."),
            ])
            response = llm.invoke(initial_prompt.format_messages(user_message=state.user_message, expected_output=state.expected_output))
            token_usage = TokenUsage(
                prompt_tokens=response.response_metadata['token_usage']['prompt_tokens'],
                completion_tokens=response.response_metadata['token_usage']['completion_tokens'],
                total_tokens=response.response_metadata['token_usage']['total_tokens']
            )
            cost = TokenTracker.calculate_openai_cost(token_usage.prompt_tokens, token_usage.completion_tokens, llm.model_name)
            api_response = APIResponse(
                content=response.content,
                token_usage=token_usage,
                cost=cost,
                thinking_time=0,
                provider='openai',
                model=llm.model_name
            )
            get_token_tracker().track_request(api_response)
            state.system_message = response.content
        else:
            update_prompt = ChatPromptTemplate.from_messages([
                ("system", "You are a prompt engineer. Improve the existing system prompt based on suggestions."),
                ("user", "Existing system prompt: {system_message}\nUser message: {user_message}\nExpected output: {expected_output}\nSuggestions: {suggestions}\n\nImproved system prompt:"),
            ])
            response = llm.invoke(update_prompt.format_messages(system_message=state.system_message, user_message=state.user_message, expected_output=state.expected_output, suggestions=state.suggestions))
            token_usage = TokenUsage(
                prompt_tokens=response.response_metadata['token_usage']['prompt_tokens'],
                completion_tokens=response.response_metadata['token_usage']['completion_tokens'],
                total_tokens=response.response_metadata['token_usage']['total_tokens']
            )
            cost = TokenTracker.calculate_openai_cost(token_usage.prompt_tokens, token_usage.completion_tokens, llm.model_name)
            api_response = APIResponse(
                content=response.content,
                token_usage=token_usage,
                cost=cost,
                thinking_time=0,
                provider='openai',
                model=llm.model_name
            )
            get_token_tracker().track_request(api_response)
            state.system_message = response.content
        logger.info(f'Generated/Updated system message: {state.system_message}')
        return state

class Evaluator(Role):
    def __init__(self, name='Evaluator'):
        super().__init__(name=name)

    @instrument_agent_action('evaluator')
    async def act(self, state: AgentState) -> AgentState:
        comparison_prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an evaluator. Determine if the output meets the acceptance criteria compared to expected."),
            ("user", "Acceptance criteria: {acceptance_criteria}\nExpected: {expected_output}\nActual: {output}\n\nDoes it meet? Say 'Yes' or 'No' at the beginning, followed by explanation."),
        ])
        response = llm.invoke(comparison_prompt.format_messages(acceptance_criteria=state.acceptance_criteria, expected_output=state.expected_output, output=state.output))
        token_usage = TokenUsage(
            prompt_tokens=response.response_metadata['token_usage']['prompt_tokens'],
            completion_tokens=response.response_metadata['token_usage']['completion_tokens'],
            total_tokens=response.response_metadata['token_usage']['total_tokens']
        )
        cost = TokenTracker.calculate_openai_cost(token_usage.prompt_tokens, token_usage.completion_tokens, llm.model_name)
        api_response = APIResponse(
            content=response.content,
            token_usage=token_usage,
            cost=cost,
            thinking_time=0,
            provider='openai',
            model=llm.model_name
        )
        get_token_tracker().track_request(api_response)
        state.analysis = response.content
        state.accepted = response.content.strip().startswith('Yes')  # improved parse
        if not state.accepted:
            suggester_prompt = ChatPromptTemplate.from_messages([
                ("system", "Suggest improvements to the system prompt based on the analysis."),
                ("user", "System prompt: {system_message}\nUser: {user_message}\nExpected: {expected_output}\nActual: {output}\nCriteria: {acceptance_criteria}\nAnalysis: {analysis}\n\nSuggestions:"),
            ])
            sug_resp = llm.invoke(suggester_prompt.format_messages(system_message=state.system_message, user_message=state.user_message, expected_output=state.expected_output, output=state.output, acceptance_criteria=state.acceptance_criteria, analysis=state.analysis))
            token_usage = TokenUsage(
                prompt_tokens=sug_resp.response_metadata['token_usage']['prompt_tokens'],
                completion_tokens=sug_resp.response_metadata['token_usage']['completion_tokens'],
                total_tokens=sug_resp.response_metadata['token_usage']['total_tokens']
            )
            cost = TokenTracker.calculate_openai_cost(token_usage.prompt_tokens, token_usage.completion_tokens, llm.model_name)
            api_response = APIResponse(
                content=sug_resp.content,
                token_usage=token_usage,
                cost=cost,
                thinking_time=0,
                provider='openai',
                model=llm.model_name
            )
            get_token_tracker().track_request(api_response)
            state.suggestions = sug_resp.content
        logger.info(f'Evaluation: {state.analysis}, Accepted: {state.accepted}')
        return state

class Optimizer(Role):
    def __init__(self, name='Optimizer'):
        super().__init__(name=name)

    @instrument_agent_action('optimizer')
    async def act(self, state: AgentState) -> AgentState:
        # Implement history analysis and best selection
        if state.best_output:
            history_prompt = ChatPromptTemplate.from_messages([
                ("system", "Compare two outputs and choose the better one based on criteria."),
                ("user", "Output A (best so far): {best_output}\nOutput B (current): {output}\nExpected: {expected_output}\nCriteria: {acceptance_criteria}\n\nWhich is better? Say 'Preferred Output ID: A' or 'Preferred Output ID: B' at the beginning, followed by why."),
            ])
            response = llm.invoke(history_prompt.format_messages(best_output=state.best_output, output=state.output, acceptance_criteria=state.acceptance_criteria, expected_output=state.expected_output))
            token_usage = TokenUsage(
                prompt_tokens=response.response_metadata['token_usage']['prompt_tokens'],
                completion_tokens=response.response_metadata['token_usage']['completion_tokens'],
                total_tokens=response.response_metadata['token_usage']['total_tokens']
            )
            cost = TokenTracker.calculate_openai_cost(token_usage.prompt_tokens, token_usage.completion_tokens, llm.model_name)
            api_response = APIResponse(
                content=response.content,
                token_usage=token_usage,
                cost=cost,
                thinking_time=0,
                provider='openai',
                model=llm.model_name
            )
            get_token_tracker().track_request(api_response)
            if 'Preferred Output ID: B' in response.content:
                state.best_output = state.output
                state.best_system_message = state.system_message
                state.best_output_age = 0
            else:
                state.best_output_age += 1
        else:
            state.best_output = state.output
            state.best_system_message = state.system_message
            state.best_output_age = 0
        logger.info(f'Optimized, Best age: {state.best_output_age}')
        return state 