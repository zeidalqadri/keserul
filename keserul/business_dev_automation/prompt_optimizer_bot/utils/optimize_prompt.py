from .metagpt_cli_wrapper import MetaGPTCLIWrapper
import uuid
import os
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

# Try to import orchestrator dependencies, but handle gracefully if not available
try:
    from .optimizer_orchestrator import OptimizerOrchestrator
    from .state import AgentState
    import asyncio
    ORCHESTRATOR_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Orchestrator dependencies not available: {e}")
    ORCHESTRATOR_AVAILABLE = False

def optimize_prompt(
    user_message: str, 
    expected_output: str, 
    acceptance_criteria: str = 'Exactly text match.',
    max_iterations: int = 10, 
    max_output_age: int = 3,
    use_legacy_cli: bool = False,
    strategy: str = 'orchestrator'  # 'orchestrator' or 'cli'
) -> str:
    """
    Unified entry point for prompt optimization.
    
    Args:
        user_message: The user message to optimize for
        expected_output: The expected output from the optimized prompt
        acceptance_criteria: Criteria for evaluation
        max_iterations: Maximum optimization iterations
        max_output_age: Maximum age for best output
        use_legacy_cli: Backward compatibility flag for legacy CLI approach
        strategy: Optimization strategy ('orchestrator' for multi-agent, 'cli' for direct CLI)
    
    Returns:
        Optimized prompt string
    """
    logger.info(f"Starting prompt optimization with strategy: {strategy}")
    
    # Backward compatibility: if use_legacy_cli is True, force CLI strategy
    if use_legacy_cli:
        strategy = 'cli'
        logger.info("Using legacy CLI mode for backward compatibility")
    
    # If orchestrator is not available, automatically fall back to CLI
    if strategy == 'orchestrator' and not ORCHESTRATOR_AVAILABLE:
        logger.warning("Orchestrator not available, falling back to CLI strategy")
        strategy = 'cli'
    
    try:
        if strategy == 'cli':
            return _optimize_with_cli(user_message, expected_output, acceptance_criteria, max_iterations, max_output_age)
        elif strategy == 'orchestrator':
            return _optimize_with_orchestrator(user_message, expected_output, acceptance_criteria, max_iterations, max_output_age)
        else:
            raise ValueError(f"Unknown optimization strategy: {strategy}")
    except Exception as e:
        logger.error(f"Optimization failed: {e}")
        if strategy == 'orchestrator':
            logger.info("Falling back to CLI strategy")
            return _optimize_with_cli(user_message, expected_output, acceptance_criteria, max_iterations, max_output_age)
        else:
            raise


def _optimize_with_cli(user_message: str, expected_output: str, acceptance_criteria: str, max_iterations: int, max_output_age: int) -> str:
    """Legacy CLI-based optimization approach"""
    logger.info("Using CLI-based optimization")
    wrapper = MetaGPTCLIWrapper()
    
    if not wrapper.health_check():
        raise RuntimeError('MetaGPT CLI health check failed')
    
    project_name = f'opt_{uuid.uuid4().hex[:8]}'
    result = wrapper.optimize_prompt(user_message, project_name)
    
    # Extract optimized prompt from result files
    optimized_prompt = result['files'].get('optimized_prompt.txt', '')
    
    if not optimized_prompt:
        # Fallback: use any .md or .txt file that might contain the optimized prompt
        for filename, content in result['files'].items():
            if filename.endswith(('.md', '.txt', '.py')) and content.strip():
                optimized_prompt = content
                break
    
    return optimized_prompt if optimized_prompt else user_message


def _optimize_with_orchestrator(user_message: str, expected_output: str, acceptance_criteria: str, max_iterations: int, max_output_age: int) -> str:
    """Multi-agent orchestrator-based optimization approach"""
    if not ORCHESTRATOR_AVAILABLE:
        raise RuntimeError("Orchestrator dependencies not available")
        
    logger.info("Using orchestrator-based optimization")
    
    # Create initial state
    initial_state = AgentState(
        user_message=user_message,
        expected_output=expected_output,
        acceptance_criteria=acceptance_criteria,
        max_iterations=max_iterations,
        max_output_age=max_output_age,
        system_message=f"Optimize this prompt for the user: {user_message}",
        iteration=0,
        accepted=False,
        best_output_age=0,
        best_system_message=""
    )
    
    # Run orchestrator
    orchestrator = OptimizerOrchestrator()
    optimized_prompt = asyncio.run(orchestrator.run_optimization(initial_state))
    
    return optimized_prompt if optimized_prompt else user_message


def get_optimization_info() -> Dict[str, Any]:
    """Get information about available optimization strategies"""
    available_strategies = ['cli']
    if ORCHESTRATOR_AVAILABLE:
        available_strategies.append('orchestrator')
        
    return {
        'strategies': available_strategies,
        'default_strategy': 'orchestrator' if ORCHESTRATOR_AVAILABLE else 'cli',
        'supports_legacy_cli': True,
        'orchestrator_available': ORCHESTRATOR_AVAILABLE,
        'version': '1.0.0'
    } 