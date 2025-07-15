from metagpt.agent import Agent
from metagpt.logs import logger
from metagpt.team import Team
from .metagpt_agents import PromptEngineer, Evaluator, Optimizer
from .state import AgentState
from langchain_openai import ChatOpenAI
import sys
from pathlib import Path
from typing import Optional
sys.path.append(str(Path(__file__).parent.parent.parent.parent / 'archive' / 'devin.cursorrules' / 'tools'))
from token_tracker import get_token_tracker, TokenUsage, APIResponse
from token_tracker import TokenTracker

executor_llm = ChatOpenAI(model_name='gpt-4o', temperature=0.01)

def prompt_executor(state: AgentState) -> AgentState:
    response = executor_llm.invoke([{'role': 'system', 'content': state.system_message}, {'role': 'user', 'content': state.user_message}])
    token_usage = TokenUsage(
        prompt_tokens=response.response_metadata['token_usage']['prompt_tokens'],
        completion_tokens=response.response_metadata['token_usage']['completion_tokens'],
        total_tokens=response.response_metadata['token_usage']['total_tokens']
    )
    cost = TokenTracker.calculate_openai_cost(token_usage.prompt_tokens, token_usage.completion_tokens, executor_llm.model_name)
    api_response = APIResponse(
        content=response.content,
        token_usage=token_usage,
        cost=cost,
        thinking_time=0,
        provider='openai',
        model=executor_llm.model_name
    )
    get_token_tracker().track_request(api_response)
    state.output = response.content
    return state

class OptimizerOrchestrator:
    def __init__(self, name='OptimizerOrchestrator'):
        self.prompt_engineer = PromptEngineer()
        self.evaluator = Evaluator()
        self.optimizer = Optimizer()

    async def run_optimization(self, initial_state: AgentState) -> str:
        state = initial_state
        while not state.accepted and state.iteration < state.max_iterations:
            state = await self.prompt_engineer.act(state)
            state = prompt_executor(state)
            state = await self.optimizer.act(state)
            if state.best_output_age >= state.max_output_age:
                break
            if state.best_output_age > 0:
                state = await self.prompt_engineer.act(state)  # from 'rerun'
                continue
            state = await self.evaluator.act(state)
            if state.accepted:
                break
            state.iteration += 1
        return state.best_system_message if state.accepted else state.system_message 