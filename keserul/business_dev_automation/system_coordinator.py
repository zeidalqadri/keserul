import argparse
import os
from langchain_openai import ChatOpenAI

# Import cost-instrumented version
try:
    from prompt_optimizer_bot.utils.cost_instrumented_wrapper import optimize_prompt
    COST_TRACKING_AVAILABLE = True
except ImportError:
    from prompt_optimizer_bot import optimize_prompt
    COST_TRACKING_AVAILABLE = False

# Import cost manager for session reporting
try:
    from shared.cost_manager import get_cost_manager
    COST_MANAGER_AVAILABLE = True
except ImportError:
    COST_MANAGER_AVAILABLE = False

# Mock LLM for demonstration
class MockLLM:
    def invoke(self, prompt):
        class MockResponse:
            def __init__(self, content):
                self.content = content
        return MockResponse(f"Mock response for: {prompt[:100]}...")

llm = MockLLM()

def main():
    parser = argparse.ArgumentParser(description='System Coordinator for Business Development Automation')
    parser.add_argument('--task', required=True, help='The task to coordinate and perform')
    parser.add_argument('--optimize-prompts', action='store_true', help='Optimize prompts before execution')
    parser.add_argument('--expected-output', default='Successful task completion', help='Expected output for prompt optimization')
    parser.add_argument('--optimization-strategy', choices=['orchestrator', 'cli'], default='orchestrator',
                       help='Strategy for prompt optimization')
    parser.add_argument('--use-legacy-cli', action='store_true', 
                       help='Use legacy CLI approach for backward compatibility')
    parser.add_argument('--acceptance-criteria', default='Task completed successfully with high quality output',
                       help='Acceptance criteria for prompt optimization')
    args = parser.parse_args()

    base_prompt = f"As the system coordinator, perform this task: {args.task}"

    if args.optimize_prompts:
        print(f"Optimizing prompts using strategy: {args.optimization_strategy}")
        try:
            optimized = optimize_prompt(
                user_message=args.task, 
                expected_output=args.expected_output,
                acceptance_criteria=args.acceptance_criteria,
                use_legacy_cli=args.use_legacy_cli,
                strategy=args.optimization_strategy
            )
            base_prompt = optimized + f"\nTask: {args.task}"
            print("Prompt optimization completed successfully")
        except Exception as e:
            print(f"Prompt optimization failed: {e}")
            print("Continuing with original prompt...")

    response = llm.invoke(base_prompt)
    print('Response:')
    print(response.content)
    
    # Print cost summary if available
    if COST_MANAGER_AVAILABLE:
        try:
            cost_manager = get_cost_manager()
            summary = cost_manager.get_session_summary()
            print(f"\n--- Cost Summary ---")
            print(f"Total Cost: ${summary['total_cost']:.6f}")
            print(f"Total Tokens: {summary['total_tokens']:,}")
            print(f"API Calls: {summary['total_api_calls']}")
            print(f"Active Operations: {summary['active_operations']}")
            print(f"Completed Operations: {summary['completed_operations']}")
        except Exception as e:
            print(f"Error getting cost summary: {e}")

if __name__ == '__main__':
    main() 