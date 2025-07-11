"""
Conversation Orchestrator for McKinsey-Insights Bot

This module provides a finite-state machine implementation for orchestrating
the conversation flow through different phases of the McKinsey-style analysis.
"""

import enum
import json
import os
import re
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from .prompt_manager import PromptTemplateManager
from .llm_client import LLMClient, LLMResponse


class ConversationState(enum.Enum):
    """States in the conversation flow."""
    
    INITIAL = "initial"
    PHASE_1 = "phase_1"  # Initial data collection
    PHASE_2 = "phase_2"  # Executive summary & key insights
    PHASE_3 = "phase_3"  # Market overview & competitive landscape
    PHASE_4 = "phase_4"  # Customer analysis & company position
    PHASE_5 = "phase_5"  # Strategic options & recommendations
    PHASE_6 = "phase_6"  # Implementation plan & expected outcomes
    FINALIZATION = "finalization"
    COMPLETE = "complete"
    ERROR = "error"


class ConversationEvent(enum.Enum):
    """Events that trigger state transitions."""
    
    START = "start"
    CONTINUE = "continue"
    FINALIZE = "finalize"
    COMPLETE = "complete"
    ERROR = "error"
    RESTART = "restart"


class ConversationContext:
    """Context for the conversation, including variables and history."""
    
    def __init__(self, variables: Dict[str, Any]):
        """
        Initialize the conversation context.
        
        Args:
            variables: Dictionary of variables for template rendering
        """
        self.variables = variables
        self.history: List[Dict[str, Any]] = []
        self.charts: List[Dict[str, Any]] = []
        self.current_phase = ConversationState.INITIAL
        self.token_usage = {
            "total": 0,
            "prompt": 0,
            "completion": 0,
            "by_phase": {}
        }
        self.cost = {
            "total": 0.0,
            "by_phase": {}
        }
        self.start_time = time.time()
        self.phase_start_times = {}
        self.phase_durations = {}
    
    def add_message(self, role: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Add a message to the conversation history.
        
        Args:
            role: Role of the message sender (system, user, assistant)
            content: Message content
            metadata: Additional metadata for the message
        """
        message = {
            "role": role,
            "content": content,
            "timestamp": time.time(),
            "metadata": metadata or {}
        }
        self.history.append(message)
    
    def add_chart(self, chart_spec: Dict[str, Any]) -> None:
        """
        Add a chart specification to the context.
        
        Args:
            chart_spec: Chart specification
        """
        self.charts.append(chart_spec)
    
    def update_token_usage(self, phase: ConversationState, prompt_tokens: int, completion_tokens: int) -> None:
        """
        Update token usage statistics.
        
        Args:
            phase: Current conversation phase
            prompt_tokens: Number of prompt tokens
            completion_tokens: Number of completion tokens
        """
        phase_name = phase.value
        
        # Update total usage
        self.token_usage["prompt"] += prompt_tokens
        self.token_usage["completion"] += completion_tokens
        self.token_usage["total"] += prompt_tokens + completion_tokens
        
        # Update phase-specific usage
        if phase_name not in self.token_usage["by_phase"]:
            self.token_usage["by_phase"][phase_name] = {
                "prompt": 0,
                "completion": 0,
                "total": 0
            }
        
        self.token_usage["by_phase"][phase_name]["prompt"] += prompt_tokens
        self.token_usage["by_phase"][phase_name]["completion"] += completion_tokens
        self.token_usage["by_phase"][phase_name]["total"] += prompt_tokens + completion_tokens
    
    def update_cost(self, phase: ConversationState, cost: float) -> None:
        """
        Update cost statistics.
        
        Args:
            phase: Current conversation phase
            cost: Cost of the API call
        """
        phase_name = phase.value
        
        # Update total cost
        self.cost["total"] += cost
        
        # Update phase-specific cost
        if phase_name not in self.cost["by_phase"]:
            self.cost["by_phase"][phase_name] = 0.0
        
        self.cost["by_phase"][phase_name] += cost
    
    def start_phase_timer(self, phase: ConversationState) -> None:
        """
        Start timing a conversation phase.
        
        Args:
            phase: Conversation phase to time
        """
        self.phase_start_times[phase.value] = time.time()
    
    def end_phase_timer(self, phase: ConversationState) -> float:
        """
        End timing a conversation phase and record the duration.
        
        Args:
            phase: Conversation phase to stop timing
            
        Returns:
            Duration of the phase in seconds
        """
        phase_name = phase.value
        if phase_name in self.phase_start_times:
            duration = time.time() - self.phase_start_times[phase_name]
            self.phase_durations[phase_name] = duration
            return duration
        return 0.0
    
    def get_last_assistant_message(self) -> Optional[Dict[str, Any]]:
        """
        Get the last message from the assistant.
        
        Returns:
            Last assistant message or None if not found
        """
        for message in reversed(self.history):
            if message["role"] == "assistant":
                return message
        return None
    
    def get_last_user_message(self) -> Optional[Dict[str, Any]]:
        """
        Get the last message from the user.
        
        Returns:
            Last user message or None if not found
        """
        for message in reversed(self.history):
            if message["role"] == "user":
                return message
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the context to a dictionary for serialization.
        
        Returns:
            Dictionary representation of the context
        """
        return {
            "variables": self.variables,
            "history": self.history,
            "charts": self.charts,
            "current_phase": self.current_phase.value,
            "token_usage": self.token_usage,
            "cost": self.cost,
            "start_time": self.start_time,
            "phase_durations": self.phase_durations,
            "total_duration": time.time() - self.start_time
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ConversationContext":
        """
        Create a context from a dictionary.
        
        Args:
            data: Dictionary representation of the context
            
        Returns:
            ConversationContext object
        """
        context = cls(data["variables"])
        context.history = data["history"]
        context.charts = data["charts"]
        context.current_phase = ConversationState(data["current_phase"])
        context.token_usage = data["token_usage"]
        context.cost = data["cost"]
        context.start_time = data["start_time"]
        context.phase_durations = data["phase_durations"]
        return context
    
    def save(self, output_path: str) -> None:
        """
        Save the context to a file.
        
        Args:
            output_path: Path to save the context
        """
        with open(output_path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)
    
    @classmethod
    def load(cls, input_path: str) -> "ConversationContext":
        """
        Load a context from a file.
        
        Args:
            input_path: Path to load the context from
            
        Returns:
            ConversationContext object
        """
        with open(input_path, "r") as f:
            data = json.load(f)
        return cls.from_dict(data)


class ConversationOrchestrator:
    """
    Orchestrates the conversation flow using a finite-state machine.
    
    This class manages the conversation through different phases of the
    McKinsey-style analysis, handling state transitions, template rendering,
    and LLM interactions.
    """
    
    def __init__(
        self,
        prompt_manager: Optional[PromptTemplateManager] = None,
        llm_client: Optional[LLMClient] = None,
        output_dir: Optional[str] = None
    ):
        """
        Initialize the conversation orchestrator.
        
        Args:
            prompt_manager: PromptTemplateManager for template rendering
            llm_client: LLMClient for LLM interactions
            output_dir: Directory to store conversation artifacts
        """
        self.prompt_manager = prompt_manager or PromptTemplateManager()
        self.llm_client = llm_client or LLMClient()
        
        if output_dir is None:
            output_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "output"
            )
        
        self.output_dir = Path(output_dir)
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Define the state machine transitions
        self.transitions = {
            ConversationState.INITIAL: {
                ConversationEvent.START: ConversationState.PHASE_1
            },
            ConversationState.PHASE_1: {
                ConversationEvent.CONTINUE: ConversationState.PHASE_2,
                ConversationEvent.ERROR: ConversationState.ERROR
            },
            ConversationState.PHASE_2: {
                ConversationEvent.CONTINUE: ConversationState.PHASE_3,
                ConversationEvent.ERROR: ConversationState.ERROR
            },
            ConversationState.PHASE_3: {
                ConversationEvent.CONTINUE: ConversationState.PHASE_4,
                ConversationEvent.ERROR: ConversationState.ERROR
            },
            ConversationState.PHASE_4: {
                ConversationEvent.CONTINUE: ConversationState.PHASE_5,
                ConversationEvent.ERROR: ConversationState.ERROR
            },
            ConversationState.PHASE_5: {
                ConversationEvent.CONTINUE: ConversationState.PHASE_6,
                ConversationEvent.ERROR: ConversationState.ERROR
            },
            ConversationState.PHASE_6: {
                ConversationEvent.FINALIZE: ConversationState.FINALIZATION,
                ConversationEvent.ERROR: ConversationState.ERROR
            },
            ConversationState.FINALIZATION: {
                ConversationEvent.COMPLETE: ConversationState.COMPLETE,
                ConversationEvent.ERROR: ConversationState.ERROR
            },
            ConversationState.ERROR: {
                ConversationEvent.RESTART: ConversationState.INITIAL
            },
            ConversationState.COMPLETE: {}  # Terminal state
        }
    
    def transition(self, context: ConversationContext, event: ConversationEvent) -> ConversationState:
        """
        Transition to a new state based on the current state and event.
        
        Args:
            context: Current conversation context
            event: Event triggering the transition
            
        Returns:
            New state after the transition
            
        Raises:
            ValueError: If the transition is not valid
        """
        current_state = context.current_phase
        
        if current_state not in self.transitions:
            raise ValueError(f"Invalid state: {current_state}")
        
        if event not in self.transitions[current_state]:
            raise ValueError(f"Invalid event {event} for state {current_state}")
        
        new_state = self.transitions[current_state][event]
        context.current_phase = new_state
        
        return new_state
    
    def start_conversation(self, variables: Dict[str, Any]) -> ConversationContext:
        """
        Start a new conversation.
        
        Args:
            variables: Variables for template rendering
            
        Returns:
            New conversation context
        """
        context = ConversationContext(variables)
        
        # Render the base prompt
        prompt = self.prompt_manager.render_base_prompt(variables)
        
        # Add the system message
        context.add_message("system", prompt)
        
        # Transition to Phase 1
        context.current_phase = ConversationState.PHASE_1
        context.start_phase_timer(ConversationState.PHASE_1)
        
        return context
    
    def process_user_message(self, context: ConversationContext, message: str) -> Tuple[str, ConversationState]:
        """
        Process a user message and generate a response.
        
        Args:
            context: Current conversation context
            message: User message
            
        Returns:
            Tuple of (assistant response, new state)
        """
        # Add the user message to the context
        context.add_message("user", message)
        
        # Check for special commands
        if message.lower() == "continue":
            if context.current_phase in [
                ConversationState.PHASE_1,
                ConversationState.PHASE_2,
                ConversationState.PHASE_3,
                ConversationState.PHASE_4,
                ConversationState.PHASE_5
            ]:
                # End timing for the current phase
                context.end_phase_timer(context.current_phase)
                
                # Transition to the next phase
                next_phase = self.transition(context, ConversationEvent.CONTINUE)
                
                # Start timing for the next phase
                context.start_phase_timer(next_phase)
                
                # Generate the prompt for the next phase
                if next_phase == ConversationState.PHASE_2:
                    prompt = self.prompt_manager.render_phase(2, context.variables)
                elif next_phase == ConversationState.PHASE_3:
                    prompt = self.prompt_manager.render_phase(3, context.variables)
                elif next_phase == ConversationState.PHASE_4:
                    prompt = self.prompt_manager.render_phase(4, context.variables)
                elif next_phase == ConversationState.PHASE_5:
                    prompt = self.prompt_manager.render_phase(5, context.variables)
                elif next_phase == ConversationState.PHASE_6:
                    prompt = self.prompt_manager.render_phase(6, context.variables)
                else:
                    prompt = "I'm not sure what to do next."
                
                # Query the LLM
                task_complexity = "medium"  # Default complexity
                
                # Adjust complexity based on phase
                if next_phase in [ConversationState.PHASE_2, ConversationState.PHASE_5]:
                    task_complexity = "high"  # Executive summary and strategic recommendations are complex
                
                response = self.llm_client.query(
                    prompt=prompt,
                    task_complexity=task_complexity
                )
                
                # Update token usage and cost
                context.update_token_usage(
                    next_phase,
                    response.token_usage.prompt_tokens,
                    response.token_usage.completion_tokens
                )
                context.update_cost(next_phase, response.cost)
                
                # Add the assistant response to the context
                context.add_message(
                    "assistant",
                    response.content,
                    {
                        "phase": next_phase.value,
                        "token_usage": response.token_usage.to_dict(),
                        "cost": response.cost,
                        "model": response.model
                    }
                )
                
                # Extract chart specifications if any
                self._extract_chart_specs(context, response.content)
                
                return response.content, next_phase
                
        elif message.lower() == "finalize" and context.current_phase == ConversationState.PHASE_6:
            # End timing for Phase 6
            context.end_phase_timer(ConversationState.PHASE_6)
            
            # Transition to finalization
            next_phase = self.transition(context, ConversationEvent.FINALIZE)
            
            # Start timing for finalization
            context.start_phase_timer(next_phase)
            
            # Generate the finalization prompt
            prompt = self.prompt_manager.render_finalization(context.variables)
            
            # Query the LLM
            response = self.llm_client.query(
                prompt=prompt,
                task_complexity="high"  # Finalization is complex
            )
            
            # Update token usage and cost
            context.update_token_usage(
                next_phase,
                response.token_usage.prompt_tokens,
                response.token_usage.completion_tokens
            )
            context.update_cost(next_phase, response.cost)
            
            # Add the assistant response to the context
            context.add_message(
                "assistant",
                response.content,
                {
                    "phase": next_phase.value,
                    "token_usage": response.token_usage.to_dict(),
                    "cost": response.cost,
                    "model": response.model
                }
            )
            
            return response.content, next_phase
            
        elif message.lower() == "complete" and context.current_phase == ConversationState.FINALIZATION:
            # End timing for finalization
            context.end_phase_timer(ConversationState.FINALIZATION)
            
            # Transition to complete
            next_phase = self.transition(context, ConversationEvent.COMPLETE)
            
            # Save the conversation context
            self._save_conversation(context)
            
            return "Conversation complete. The deck has been generated.", next_phase
        
        else:
            # For regular messages, query the LLM with the current context
            prompt = self._build_prompt_from_history(context)
            prompt += f"\nUser: {message}\n\nAssistant: "
            
            # Query the LLM
            response = self.llm_client.query(
                prompt=prompt,
                task_complexity="medium"
            )
            
            # Update token usage and cost
            context.update_token_usage(
                context.current_phase,
                response.token_usage.prompt_tokens,
                response.token_usage.completion_tokens
            )
            context.update_cost(context.current_phase, response.cost)
            
            # Add the assistant response to the context
            context.add_message(
                "assistant",
                response.content,
                {
                    "phase": context.current_phase.value,
                    "token_usage": response.token_usage.to_dict(),
                    "cost": response.cost,
                    "model": response.model
                }
            )
            
            # Extract chart specifications if any
            self._extract_chart_specs(context, response.content)
            
            return response.content, context.current_phase
    
    def _build_prompt_from_history(self, context: ConversationContext) -> str:
        """
        Build a prompt from the conversation history.
        
        Args:
            context: Conversation context
            
        Returns:
            Prompt string
        """
        prompt = ""
        
        # Add the system message
        for message in context.history:
            if message["role"] == "system":
                prompt += f"{message['content']}\n\n"
                break
        
        # Add the conversation history (excluding system messages)
        for message in context.history:
            if message["role"] == "user":
                prompt += f"User: {message['content']}\n\n"
            elif message["role"] == "assistant":
                prompt += f"Assistant: {message['content']}\n\n"
        
        return prompt
    
    def _extract_chart_specs(self, context: ConversationContext, content: str) -> None:
        """
        Extract chart specifications from the assistant's response.
        
        Args:
            context: Conversation context
            content: Assistant's response
        """
        # Look for chart specifications in the format:
        # ## Chart Specification
        # ...
        # (chart details)
        # ...
        chart_sections = re.findall(
            r"## Chart Specification\s+(.*?)(?=##|\Z)",
            content,
            re.DOTALL
        )
        
        for section in chart_sections:
            # Parse the chart specification
            chart_spec = {}
            
            # Extract chart title
            title_match = re.search(r"For the (.*?) chart:", section)
            if title_match:
                chart_spec["title"] = title_match.group(1).strip()
            
            # Extract chart type
            type_match = re.search(r"\*\*Chart Type\*\*: (.*?)$", section, re.MULTILINE)
            if type_match:
                chart_spec["type"] = type_match.group(1).strip()
            
            # Extract data series
            data_series = []
            series_matches = re.findall(r"- (.*?): (.*?)$", section, re.MULTILINE)
            for name, values in series_matches:
                # Try to parse values as a list of numbers
                try:
                    values_list = [float(x.strip()) for x in values.strip("[]").split(",")]
                except ValueError:
                    values_list = values.strip()
                
                data_series.append({
                    "name": name.strip(),
                    "values": values_list
                })
            
            if data_series:
                chart_spec["data_series"] = data_series
            
            # Extract axes
            x_axis_match = re.search(r"\*\*X-Axis\*\*: (.*?)$", section, re.MULTILINE)
            if x_axis_match:
                chart_spec["x_axis"] = x_axis_match.group(1).strip()
            
            y_axis_match = re.search(r"\*\*Y-Axis\*\*: (.*?)$", section, re.MULTILINE)
            if y_axis_match:
                chart_spec["y_axis"] = y_axis_match.group(1).strip()
            
            # Extract colors
            colors_match = re.search(r"\*\*Colors\*\*: Primary: (.*?), Secondary: (.*?)$", section, re.MULTILINE)
            if colors_match:
                chart_spec["primary_color"] = colors_match.group(1).strip()
                chart_spec["secondary_color"] = colors_match.group(2).strip()
            
            # Extract labels and legend
            labels_match = re.search(r"\*\*Labels\*\*: (.*?)$", section, re.MULTILINE)
            if labels_match:
                chart_spec["include_labels"] = labels_match.group(1).strip().lower() == "true"
            
            legend_match = re.search(r"\*\*Legend\*\*: (.*?)$", section, re.MULTILINE)
            if legend_match:
                chart_spec["include_legend"] = legend_match.group(1).strip().lower() == "true"
            
            # Extract notes
            notes_match = re.search(r"\*\*Notes\*\*: (.*?)$", section, re.MULTILINE)
            if notes_match:
                chart_spec["notes"] = notes_match.group(1).strip()
            
            # Extract description (everything after the structured fields)
            description_match = re.search(r"\*\*Notes\*\*:.*?\n\n(.*?)$", section, re.DOTALL)
            if description_match:
                chart_spec["description"] = description_match.group(1).strip()
            
            # Add the chart specification to the context
            if chart_spec:
                context.add_chart(chart_spec)
    
    def _save_conversation(self, context: ConversationContext) -> str:
        """
        Save the conversation context to a file.
        
        Args:
            context: Conversation context
            
        Returns:
            Path to the saved file
        """
        # Create a unique filename based on the company name and timestamp
        company_name = context.variables.get("company_name", "company").lower().replace(" ", "_")
        timestamp = int(time.time())
        filename = f"{company_name}_{timestamp}.json"
        
        # Save the context
        output_path = self.output_dir / filename
        context.save(str(output_path))
        
        return str(output_path)
    
    def generate_deck(self, context: ConversationContext) -> str:
        """
        Generate a slide deck from the conversation context.
        
        Args:
            context: Conversation context
            
        Returns:
            Path to the generated deck
            
        Note:
            This is a placeholder method. The actual implementation will be in the DeckAssembler class.
        """
        # This is a placeholder. The actual implementation will be in the DeckAssembler class.
        return "Deck generation not implemented yet." 