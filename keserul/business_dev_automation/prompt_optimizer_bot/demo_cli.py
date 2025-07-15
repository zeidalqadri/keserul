import argparse
import sys
import os

# Add the parent directory to the path so we can import prompt_optimizer_bot
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from prompt_optimizer_bot import optimize_prompt, get_optimization_info

def main():
    parser = argparse.ArgumentParser(description='Demo CLI for Prompt Optimization')
    parser.add_argument('--user_message', help='The user message to optimize for')
    parser.add_argument('--expected_output', help='The expected output from the optimized prompt')
    parser.add_argument('--acceptance_criteria', default='Exactly text match.', help='Acceptance criteria for evaluation')
    parser.add_argument('--max_iterations', type=int, default=10, help='Maximum optimization iterations')
    parser.add_argument('--max_output_age', type=int, default=3, help='Maximum age for best output')
    parser.add_argument('--use_legacy_cli', action='store_true', help='Use legacy CLI approach for backward compatibility')
    parser.add_argument('--strategy', choices=['orchestrator', 'cli'], default='orchestrator', 
                       help='Optimization strategy to use')
    parser.add_argument('--info', action='store_true', help='Show optimization information and exit')
    args = parser.parse_args()
    
    if args.info:
        info = get_optimization_info()
        print('Prompt Optimization Information:')
        print(f"Available strategies: {', '.join(info['strategies'])}")
        print(f"Default strategy: {info['default_strategy']}")
        print(f"Supports legacy CLI: {info['supports_legacy_cli']}")
        print(f"Orchestrator available: {info['orchestrator_available']}")
        print(f"Version: {info['version']}")
        return 0
    
    # If not showing info, require user_message and expected_output
    if not args.user_message or not args.expected_output:
        parser.error('--user_message and --expected_output are required unless using --info')
    
    print(f"Starting optimization with strategy: {args.strategy}")
    if args.use_legacy_cli:
        print("Using legacy CLI mode for backward compatibility")
    
    try:
        optimized_prompt = optimize_prompt(
            args.user_message,
            args.expected_output,
            acceptance_criteria=args.acceptance_criteria,
            max_iterations=args.max_iterations,
            max_output_age=args.max_output_age,
            use_legacy_cli=args.use_legacy_cli,
            strategy=args.strategy
        )
        print('Optimized System Prompt:')
        print(optimized_prompt)
    except Exception as e:
        print(f'Error during optimization: {e}')
        return 1
    
    return 0

if __name__ == '__main__':
    exit(main()) 