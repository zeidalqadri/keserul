"""
Cost-instrumented wrapper for MetaGPT optimization functions

This module provides instrumented versions of the optimization functions
that integrate with the cost management system and Prometheus metrics.
"""

import logging
import time
import uuid
from typing import Optional, Dict, Any
from functools import wraps

# Import the cost manager
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

try:
    from shared.cost_manager import get_cost_manager, track_metagpt_event, CostReport
    COST_MANAGER_AVAILABLE = True
except ImportError:
    COST_MANAGER_AVAILABLE = False
    logging.warning("Cost manager not available. Cost tracking will be disabled.")

# Import the original optimization functions
from .optimize_prompt import optimize_prompt as _original_optimize_prompt
from .optimize_prompt import _optimize_with_orchestrator as _original_orchestrator
from .optimize_prompt import _optimize_with_cli as _original_cli

logger = logging.getLogger(__name__)

def cost_instrumented_optimize_prompt(
    user_message: str, 
    expected_output: str, 
    acceptance_criteria: str = 'Exactly text match.',
    max_iterations: int = 10, 
    max_output_age: int = 3,
    use_legacy_cli: bool = False,
    strategy: str = 'orchestrator'
) -> str:
    """
    Cost-instrumented version of optimize_prompt that tracks costs and MetaGPT events.
    
    This wrapper:
    1. Starts cost tracking for the optimization operation
    2. Tracks MetaGPT events (optimization cycles, agent actions)
    3. Captures all API costs during the optimization process
    4. Completes cost tracking and returns the optimized prompt
    """
    
    if not COST_MANAGER_AVAILABLE:
        logger.warning("Cost manager not available. Using original optimize_prompt.")
        return _original_optimize_prompt(
            user_message, expected_output, acceptance_criteria,
            max_iterations, max_output_age, use_legacy_cli, strategy
        )
    
    # Generate unique operation ID
    operation_id = f"prompt_optimization_{uuid.uuid4().hex[:8]}"
    
    # Start cost tracking
    cost_manager = get_cost_manager()
    cost_report = cost_manager.start_operation(
        operation_id,
        metadata={
            'strategy': strategy,
            'use_legacy_cli': use_legacy_cli,
            'max_iterations': max_iterations,
            'max_output_age': max_output_age,
            'user_message_length': len(user_message),
            'expected_output_length': len(expected_output),
            'acceptance_criteria_length': len(acceptance_criteria)
        }
    )
    
    # Track optimization cycle start
    track_metagpt_event(
        'optimization_cycle',
        strategy=strategy,
        status='started'
    )
    
    try:
        # Call the original function
        result = _original_optimize_prompt(
            user_message, expected_output, acceptance_criteria,
            max_iterations, max_output_age, use_legacy_cli, strategy
        )
        
        # Track successful completion
        track_metagpt_event(
            'optimization_cycle',
            strategy=strategy,
            status='completed'
        )
        
        logger.info(f"Optimization completed successfully. Operation: {operation_id}")
        return result
        
    except Exception as e:
        # Track failed completion
        track_metagpt_event(
            'optimization_cycle',
            strategy=strategy,
            status='failed'
        )
        
        logger.error(f"Optimization failed. Operation: {operation_id}, Error: {e}")
        raise
        
    finally:
        # Complete cost tracking
        final_report = cost_manager.complete_operation(operation_id)
        if final_report:
            logger.info(
                f"Optimization cost report - Operation: {operation_id}, "
                f"Cost: ${final_report.total_cost:.6f}, "
                f"Tokens: {final_report.total_tokens}, "
                f"Duration: {final_report.duration():.2f}s, "
                f"API Calls: {final_report.api_calls}"
            )

def cost_instrumented_orchestrator(
    user_message: str, 
    expected_output: str, 
    acceptance_criteria: str, 
    max_iterations: int, 
    max_output_age: int
) -> str:
    """Cost-instrumented version of _optimize_with_orchestrator"""
    
    if not COST_MANAGER_AVAILABLE:
        return _original_orchestrator(
            user_message, expected_output, acceptance_criteria,
            max_iterations, max_output_age
        )
    
    operation_id = f"orchestrator_optimization_{uuid.uuid4().hex[:8]}"
    
    cost_manager = get_cost_manager()
    cost_report = cost_manager.start_operation(
        operation_id,
        metadata={
            'strategy': 'orchestrator',
            'max_iterations': max_iterations,
            'max_output_age': max_output_age
        }
    )
    
    track_metagpt_event('agent_action', agent_type='orchestrator', action='started')
    
    try:
        result = _original_orchestrator(
            user_message, expected_output, acceptance_criteria,
            max_iterations, max_output_age
        )
        
        track_metagpt_event('agent_action', agent_type='orchestrator', action='completed')
        return result
        
    except Exception as e:
        track_metagpt_event('agent_action', agent_type='orchestrator', action='failed')
        raise
        
    finally:
        cost_manager.complete_operation(operation_id)

def cost_instrumented_cli(
    user_message: str, 
    expected_output: str, 
    acceptance_criteria: str, 
    max_iterations: int, 
    max_output_age: int
) -> str:
    """Cost-instrumented version of _optimize_with_cli"""
    
    if not COST_MANAGER_AVAILABLE:
        return _original_cli(
            user_message, expected_output, acceptance_criteria,
            max_iterations, max_output_age
        )
    
    operation_id = f"cli_optimization_{uuid.uuid4().hex[:8]}"
    
    cost_manager = get_cost_manager()
    cost_report = cost_manager.start_operation(
        operation_id,
        metadata={
            'strategy': 'cli',
            'max_iterations': max_iterations,
            'max_output_age': max_output_age
        }
    )
    
    track_metagpt_event('agent_action', agent_type='cli_wrapper', action='started')
    
    try:
        result = _original_cli(
            user_message, expected_output, acceptance_criteria,
            max_iterations, max_output_age
        )
        
        track_metagpt_event('agent_action', agent_type='cli_wrapper', action='completed')
        return result
        
    except Exception as e:
        track_metagpt_event('agent_action', agent_type='cli_wrapper', action='failed')
        raise
        
    finally:
        cost_manager.complete_operation(operation_id)

def instrument_agent_action(agent_type: str):
    """Decorator to instrument individual agent actions"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            if not COST_MANAGER_AVAILABLE:
                return await func(*args, **kwargs)
            
            action_id = f"{agent_type}_action_{uuid.uuid4().hex[:8]}"
            
            cost_manager = get_cost_manager()
            cost_report = cost_manager.start_operation(
                action_id,
                metadata={'agent_type': agent_type}
            )
            
            track_metagpt_event('agent_action', agent_type=agent_type, action='started')
            
            try:
                result = await func(*args, **kwargs)
                track_metagpt_event('agent_action', agent_type=agent_type, action='completed')
                return result
                
            except Exception as e:
                track_metagpt_event('agent_action', agent_type=agent_type, action='failed')
                raise
                
            finally:
                cost_manager.complete_operation(action_id)
                
        return wrapper
    return decorator

# Export the instrumented functions
optimize_prompt = cost_instrumented_optimize_prompt
_optimize_with_orchestrator = cost_instrumented_orchestrator
_optimize_with_cli = cost_instrumented_cli 