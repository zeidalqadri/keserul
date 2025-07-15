"""
PromptOptimizer-Bot

A tool for optimizing LLM prompts using MetaGPT multi-agent framework.
"""

__version__ = "0.1.0"

# Always available imports
from .utils.optimize_prompt import optimize_prompt, get_optimization_info

# Conditional imports for orchestrator components
__all__ = [
    "optimize_prompt",
    "get_optimization_info",
]

try:
    from .utils.optimizer_orchestrator import OptimizerOrchestrator
    from .utils.metagpt_agents import PromptEngineer, Evaluator, Optimizer
    
    __all__.extend([
        "OptimizerOrchestrator",
        "PromptEngineer",
        "Evaluator",
        "Optimizer",
    ])
except ImportError:
    # MetaGPT dependencies not available, only CLI functionality will be available
    pass 