#!/usr/bin/env python
"""
Command-line interface for the McKinsey-Insights Bot.

This module provides a simple command-line interface for interacting with
the McKinsey-Insights Bot, allowing users to conduct conversations and
generate PowerPoint presentations.
"""

import argparse
import os
import sys
import time
from pathlib import Path

from .utils.conversation_orchestrator import ConversationOrchestrator, ConversationState
from .utils.deck_assembler import DeckAssembler
from .utils.llm_client import LLMClient
from .utils.prompt_manager import PromptTemplateManager


def parse_args():
    """
    Parse command-line arguments.
    
    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(description="McKinsey-Insights Bot CLI")
    
    parser.add_argument(
        "--company",
        type=str,
        required=True,
        help="Company name"
    )
    
    parser.add_argument(
        "--market",
        type=str,
        required=True,
        help="Market segment"
    )
    
    parser.add_argument(
        "--region",
        type=str,
        required=True,
        help="Geographic region"
    )
    
    parser.add_argument(
        "--period",
        type=str,
        required=True,
        help="Time period for analysis"
    )
    
    parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help="Directory to save output files"
    )
    
    parser.add_argument(
        "--template",
        type=str,
        default=None,
        help="Path to PowerPoint template"
    )
    
    parser.add_argument(
        "--budget",
        type=float,
        default=None,
        help="Maximum budget for the conversation (in USD)"
    )
    
    parser.add_argument(
        "--save-context",
        action="store_true",
        help="Save conversation context after each message"
    )
    
    parser.add_argument(
        "--load-context",
        type=str,
        default=None,
        help="Load conversation context from a file"
    )
    
    return parser.parse_args()


def print_banner():
    """Print the banner."""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║                   McKinsey-Insights Bot                      ║
║                                                              ║
║  Generate McKinsey-style market analysis and presentations   ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
"""
    print(banner)


def print_phase_info(phase):
    """
    Print information about the current phase.
    
    Args:
        phase: Current conversation phase
    """
    phase_info = {
        ConversationState.INITIAL: {
            "name": "Initial Setup",
            "description": "Setting up the conversation"
        },
        ConversationState.PHASE_1: {
            "name": "Phase 1: Initial Data Collection",
            "description": "Gathering information about the company, market, and objectives"
        },
        ConversationState.PHASE_2: {
            "name": "Phase 2: Executive Summary & Key Insights",
            "description": "High-level overview and key findings"
        },
        ConversationState.PHASE_3: {
            "name": "Phase 3: Market Overview & Competitive Landscape",
            "description": "Market size, growth, trends, and competitors"
        },
        ConversationState.PHASE_4: {
            "name": "Phase 4: Customer Analysis & Company Position",
            "description": "Customer segments, needs, and company positioning"
        },
        ConversationState.PHASE_5: {
            "name": "Phase 5: Strategic Options & Recommendations",
            "description": "Strategic alternatives and recommended approach"
        },
        ConversationState.PHASE_6: {
            "name": "Phase 6: Implementation Plan & Expected Outcomes",
            "description": "Action steps and projected results"
        },
        ConversationState.FINALIZATION: {
            "name": "Finalization",
            "description": "Finalizing the analysis and preparing for deck generation"
        },
        ConversationState.COMPLETE: {
            "name": "Complete",
            "description": "Analysis complete"
        },
        ConversationState.ERROR: {
            "name": "Error",
            "description": "An error occurred"
        }
    }
    
    info = phase_info.get(phase, {
        "name": str(phase),
        "description": "Unknown phase"
    })
    
    print("\n" + "=" * 80)
    print(f"Current Phase: {info['name']}")
    print(f"Description: {info['description']}")
    print("=" * 80 + "\n")


def print_help():
    """Print help information."""
    print("\nCommands:")
    print("  help       - Show this help message")
    print("  continue   - Continue to the next phase")
    print("  finalize   - Finalize the analysis (only in Phase 6)")
    print("  complete   - Generate the deck (only in Finalization phase)")
    print("  stats      - Show token usage and cost statistics")
    print("  save       - Save the conversation context to a file")
    print("  quit       - Exit the program")
    print()


def print_stats(context):
    """
    Print token usage and cost statistics.
    
    Args:
        context: Conversation context
    """
    print("\nToken Usage:")
    print(f"  Total: {context.token_usage['total']} tokens")
    print(f"  Prompt: {context.token_usage['prompt']} tokens")
    print(f"  Completion: {context.token_usage['completion']} tokens")
    
    print("\nToken Usage by Phase:")
    for phase, usage in context.token_usage["by_phase"].items():
        print(f"  {phase}: {usage['total']} tokens")
    
    print("\nCost:")
    print(f"  Total: ${context.cost['total']:.4f}")
    
    print("\nCost by Phase:")
    for phase, cost in context.cost["by_phase"].items():
        print(f"  {phase}: ${cost:.4f}")
    
    print("\nTime:")
    total_duration = time.time() - context.start_time
    print(f"  Total: {total_duration:.2f} seconds")
    
    print("\nTime by Phase:")
    for phase, duration in context.phase_durations.items():
        print(f"  {phase}: {duration:.2f} seconds")
    
    print()


def save_context(context, output_dir):
    """
    Save the conversation context to a file.
    
    Args:
        context: Conversation context
        output_dir: Output directory
        
    Returns:
        Path to the saved file
    """
    os.makedirs(output_dir, exist_ok=True)
    
    company_name = context.variables.get("company_name", "company").lower().replace(" ", "_")
    timestamp = int(time.time())
    filename = f"{company_name}_{timestamp}.json"
    
    output_path = os.path.join(output_dir, filename)
    context.save(output_path)
    
    print(f"Context saved to: {output_path}")
    return output_path


def main():
    """Main function."""
    args = parse_args()
    
    print_banner()
    
    # Set up output directory
    if args.output_dir is None:
        output_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "output"
        )
    else:
        output_dir = args.output_dir
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize components
    prompt_manager = PromptTemplateManager()
    llm_client = LLMClient(budget_ceiling=args.budget)
    orchestrator = ConversationOrchestrator(
        prompt_manager=prompt_manager,
        llm_client=llm_client,
        output_dir=output_dir
    )
    deck_assembler = DeckAssembler(
        template_path=args.template,
        output_dir=output_dir
    )
    
    # Load or create conversation context
    if args.load_context:
        try:
            context = orchestrator.ConversationContext.load(args.load_context)
            print(f"Loaded conversation context from: {args.load_context}")
        except Exception as e:
            print(f"Error loading context: {e}")
            sys.exit(1)
    else:
        # Create variables
        variables = {
            "company_name": args.company,
            "market_segment": args.market,
            "region": args.region,
            "time_period": args.period
        }
        
        # Start the conversation
        context = orchestrator.start_conversation(variables)
        print("Started new conversation")
    
    # Print the current phase
    print_phase_info(context.current_phase)
    print_help()
    
    # Main loop
    while True:
        if context.current_phase == ConversationState.COMPLETE:
            print("Analysis complete!")
            break
        
        # Get user input
        try:
            user_input = input("\nYou: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting...")
            break
        
        # Process commands
        if user_input.lower() == "quit":
            print("Exiting...")
            break
        elif user_input.lower() == "help":
            print_help()
            continue
        elif user_input.lower() == "stats":
            print_stats(context)
            continue
        elif user_input.lower() == "save":
            save_context(context, output_dir)
            continue
        
        # Process the message
        try:
            response, new_state = orchestrator.process_user_message(context, user_input)
            
            # Print the response
            print(f"\nAssistant: {response}")
            
            # If the state changed, print the new phase info
            if new_state != context.current_phase:
                print_phase_info(new_state)
            
            # Save the context if requested
            if args.save_context:
                save_context(context, output_dir)
            
            # If the conversation is complete, generate the deck
            if new_state == ConversationState.COMPLETE:
                print("\nGenerating PowerPoint deck...")
                
                presentation = deck_assembler.create_presentation(context.to_dict())
                
                company_name = context.variables.get("company_name", "company").lower().replace(" ", "_")
                filename = f"{company_name}_analysis.pptx"
                
                output_path = deck_assembler.save_presentation(presentation, filename)
                print(f"Deck saved to: {output_path}")
                
                # Print final statistics
                print("\nFinal Statistics:")
                print_stats(context)
                
                break
        
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main() 