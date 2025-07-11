"""
LLM Client for McKinsey-Insights Bot

This module provides a client for interacting with various LLM providers,
with support for cost tracking, model selection, and token usage monitoring.
"""

import json
import os
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

# Optional .env loading
try:
    from dotenv import load_dotenv  # type: ignore  # Optional dependency
    load_dotenv()
except ImportError:
    pass

try:
    import tiktoken  # type: ignore
except ImportError:
    tiktoken = None  # Optional; fallback estimation will be used
    # Note: Avoid runtime package installation inside library code to
    #       ensure compatibility with restricted or CI environments.

try:
    from openai import OpenAI  # type: ignore  # Optional dependency
except ImportError:
    OpenAI = None  # Optional; will fallback to mock implementation if absent
    # Avoid attempting to install packages at runtime in restricted environments.


class TokenUsage:
    """Track token usage for a single API call."""
    
    def __init__(
        self,
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
        total_tokens: int = 0,
    ):
        self.prompt_tokens = prompt_tokens
        self.completion_tokens = completion_tokens
        self.total_tokens = total_tokens or (prompt_tokens + completion_tokens)
    
    def to_dict(self) -> Dict[str, int]:
        """Convert to dictionary representation."""
        return {
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.total_tokens,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, int]) -> "TokenUsage":
        """Create from dictionary representation."""
        return cls(
            prompt_tokens=data.get("prompt_tokens", 0),
            completion_tokens=data.get("completion_tokens", 0),
            total_tokens=data.get("total_tokens", 0),
        )


class LLMResponse:
    """Response from an LLM API call with metadata."""
    
    def __init__(
        self,
        content: str,
        token_usage: TokenUsage,
        cost: float,
        model: str,
        provider: str,
        thinking_time: float,
    ):
        self.content = content
        self.token_usage = token_usage
        self.cost = cost
        self.model = model
        self.provider = provider
        self.thinking_time = thinking_time
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "content": self.content,
            "token_usage": self.token_usage.to_dict(),
            "cost": self.cost,
            "model": self.model,
            "provider": self.provider,
            "thinking_time": self.thinking_time,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LLMResponse":
        """Create from dictionary representation."""
        return cls(
            content=data["content"],
            token_usage=TokenUsage.from_dict(data["token_usage"]),
            cost=data["cost"],
            model=data["model"],
            provider=data["provider"],
            thinking_time=data["thinking_time"],
        )


class LLMClient:
    """
    Client for interacting with LLM APIs with cost tracking and model selection.
    
    Features:
    - Multiple model support (OpenAI, local models)
    - Cost tracking and budgeting
    - Token usage monitoring
    - Automatic model selection based on task complexity
    """
    
    # Cost per 1K tokens for different models (in USD)
    # Source: https://openai.com/pricing
    MODEL_COSTS = {
        # OpenAI models
        "gpt-4o": {"input": 0.005, "output": 0.015},
        "gpt-4-turbo": {"input": 0.01, "output": 0.03},
        "gpt-4": {"input": 0.03, "output": 0.06},
        "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
        
        # Local models (free)
        "local-llama": {"input": 0.0, "output": 0.0},
        "local-mistral": {"input": 0.0, "output": 0.0},
    }
    
    def __init__(
        self,
        config_path: Optional[str] = None,
        max_budget: Optional[float] = None,
        default_model: str = "gpt-4o",
        log_dir: Optional[str] = None,
    ):
        """
        Initialize the LLM client.
        
        Args:
            config_path: Path to the configuration file
            max_budget: Maximum budget in USD
            default_model: Default model to use
            log_dir: Directory to store logs
        """
        self.default_model = default_model
        self.max_budget = max_budget
        self.total_cost = 0.0
        self.total_tokens = 0
        self.call_history: List[Dict[str, Any]] = []
        
        # Load configuration
        self.config = self._load_config(config_path)
        
        # Set up logging
        self.log_dir = Path(log_dir) if log_dir else Path("logs")
        os.makedirs(self.log_dir, exist_ok=True)
        
        # Initialize clients
        self.openai_client = self._init_openai_client()
    
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load configuration from file or use defaults."""
        if config_path and os.path.exists(config_path):
            with open(config_path, "r") as f:
                return json.load(f)
        
        # Default configuration
        return {
            "max_budget": self.max_budget or 10.0,  # USD
            "default_model": self.default_model,
            "models": {
                "cheap": "gpt-3.5-turbo",
                "balanced": "gpt-4o",
                "powerful": "gpt-4-turbo",
            },
        }
    
    def _init_openai_client(self) -> Optional[Any]:
        """Initialize OpenAI client if API key is available and OpenAI package present."""
        if OpenAI is None:
            return None
        api_key = os.environ.get("OPENAI_API_KEY")
        if api_key:
            return OpenAI(api_key=api_key)
        return None
    
    def _estimate_tokens(self, text: str, model: str = "gpt-4o") -> int:
        """Estimate the number of tokens in a text string."""
        if tiktoken is None:
            # Fallback to simple tokenization if tiktoken is not available
            return len(text) // 4
        try:
            encoding = tiktoken.encoding_for_model(model)
            return len(encoding.encode(text))
        except Exception:
            # Fallback: rough estimate based on words
            return len(text) // 4
    
    def _calculate_cost(
        self, prompt_tokens: int, completion_tokens: int, model: str
    ) -> float:
        """Calculate the cost of an API call."""
        if model not in self.MODEL_COSTS:
            # Default to gpt-4o pricing if model not found
            model = "gpt-4o"
        
        costs = self.MODEL_COSTS[model]
        prompt_cost = (prompt_tokens / 1000) * costs["input"]
        completion_cost = (completion_tokens / 1000) * costs["output"]
        
        return prompt_cost + completion_cost
    
    def _check_budget(self, estimated_cost: float) -> bool:
        """Check if the estimated cost is within budget."""
        if self.max_budget is None:
            return True
        
        if self.total_cost + estimated_cost > self.max_budget:
            return False
        
        return True
    
    def _select_model(self, task_complexity: str, prompt_length: int) -> str:
        """
        Select the appropriate model based on task complexity and prompt length.
        
        Args:
            task_complexity: "low", "medium", or "high"
            prompt_length: Length of the prompt in characters
            
        Returns:
            Model name to use
        """
        models = self.config["models"]
        
        # For very short prompts, use the cheap model
        if prompt_length < 500 and task_complexity == "low":
            return models["cheap"]
        
        # For high complexity tasks, use the powerful model
        if task_complexity == "high":
            return models["powerful"]
        
        # Default to the balanced model
        return models["balanced"]
    
    def _log_api_call(self, response: LLMResponse) -> None:
        """Log an API call to the history and file."""
        # Add to history
        self.call_history.append(response.to_dict())
        
        # Update totals
        self.total_cost += response.cost
        self.total_tokens += response.token_usage.total_tokens
        
        # Log to file
        log_file = self.log_dir / "api_calls.jsonl"
        with open(log_file, "a") as f:
            f.write(json.dumps(response.to_dict()) + "\n")
    
    def query(
        self,
        prompt: str,
        model: Optional[str] = None,
        task_complexity: str = "medium",
        max_tokens: int = 2000,
        temperature: float = 0.7,
    ) -> LLMResponse:
        """
        Query an LLM with a prompt.
        
        Args:
            prompt: The prompt to send to the LLM
            model: The model to use (overrides automatic selection)
            task_complexity: "low", "medium", or "high"
            max_tokens: Maximum number of tokens to generate
            temperature: Temperature parameter for generation
            
        Returns:
            LLMResponse object with content and metadata
            
        Raises:
            ValueError: If budget exceeded or API error
        """
        # Select model if not specified
        if model is None:
            model = self._select_model(task_complexity, len(prompt))
        
        # Estimate tokens and cost
        estimated_prompt_tokens = self._estimate_tokens(prompt, model)
        estimated_completion_tokens = max_tokens
        estimated_cost = self._calculate_cost(
            estimated_prompt_tokens, estimated_completion_tokens, model
        )
        
        # Check budget
        if not self._check_budget(estimated_cost):
            raise ValueError(
                f"Budget exceeded: {self.total_cost:.2f} + {estimated_cost:.2f} > {self.max_budget:.2f}"
            )
        
        # Query the LLM
        start_time = time.time()
        
        if model.startswith("gpt"):
            if self.openai_client is None:
                raise ValueError("OpenAI API key not found")
            
            response = self.openai_client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature,
            )
            
            content = response.choices[0].message.content
            token_usage = TokenUsage(
                prompt_tokens=response.usage.prompt_tokens,
                completion_tokens=response.usage.completion_tokens,
                total_tokens=response.usage.total_tokens,
            )
            
            # Calculate actual cost
            cost = self._calculate_cost(
                token_usage.prompt_tokens, token_usage.completion_tokens, model
            )
            
        elif model.startswith("local"):
            # Simulate local model response
            # In a real implementation, this would call a local API
            content = f"[Local model {model} response - This is a placeholder]"
            token_usage = TokenUsage(
                prompt_tokens=estimated_prompt_tokens,
                completion_tokens=len(content) // 4,
            )
            cost = 0.0
        else:
            raise ValueError(f"Unsupported model: {model}")
        
        thinking_time = time.time() - start_time
        
        # Create response object
        response = LLMResponse(
            content=content,
            token_usage=token_usage,
            cost=cost,
            model=model,
            provider="openai" if model.startswith("gpt") else "local",
            thinking_time=thinking_time,
        )
        
        # Log the API call
        self._log_api_call(response)
        
        return response
    
    def get_usage_summary(self) -> Dict[str, Any]:
        """Get a summary of API usage."""
        model_usage = {}
        for call in self.call_history:
            model = call["model"]
            if model not in model_usage:
                model_usage[model] = {
                    "calls": 0,
                    "tokens": 0,
                    "cost": 0.0,
                }
            
            model_usage[model]["calls"] += 1
            model_usage[model]["tokens"] += call["token_usage"]["total_tokens"]
            model_usage[model]["cost"] += call["cost"]
        
        return {
            "total_calls": len(self.call_history),
            "total_tokens": self.total_tokens,
            "total_cost": self.total_cost,
            "budget_remaining": (self.max_budget - self.total_cost) if self.max_budget else None,
            "model_usage": model_usage,
        }
    
    def save_usage_summary(self, output_path: Optional[str] = None) -> str:
        """
        Save usage summary to a JSON file.
        
        Args:
            output_path: Path to save the summary
            
        Returns:
            Path to the saved file
        """
        if output_path is None:
            output_path = str(self.log_dir / "usage_summary.json")

        summary = self.get_usage_summary()

        # Ensure output_path is a string or Path, and create parent dirs if needed
        output_path_obj = Path(output_path)
        output_path_obj.parent.mkdir(parents=True, exist_ok=True)

        with open(str(output_path), "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)
        
        return str(output_path) 