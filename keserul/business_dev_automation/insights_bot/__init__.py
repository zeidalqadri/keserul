"""
McKinsey-Insights Bot

A powerful tool for generating McKinsey-style market analysis and strategic recommendations
with automated PowerPoint deck creation.
"""

__version__ = "0.1.0"
__author__ = "Business Development Automation Team"

from .utils.conversation_orchestrator import ConversationOrchestrator, ConversationContext, ConversationState, ConversationEvent
from .utils.deck_assembler import DeckAssembler
from .utils.llm_client import LLMClient, LLMResponse, TokenUsage
from .utils.prompt_manager import PromptTemplateManager

__all__ = [
    "ConversationOrchestrator",
    "ConversationContext",
    "ConversationState",
    "ConversationEvent",
    "DeckAssembler",
    "LLMClient",
    "LLMResponse",
    "TokenUsage",
    "PromptTemplateManager"
]
