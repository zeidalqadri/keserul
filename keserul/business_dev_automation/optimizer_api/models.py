from pydantic import BaseModel, Field
from typing import Optional, List

class PromptRequest(BaseModel):
    prompt: str = Field(..., description="The prompt string to be optimized.")
    strategy: Optional[str] = Field(None, description="Optional optimization strategy (e.g., 'orchestrator', 'cli').")

class PromptResponse(BaseModel):
    optimized_prompt: str = Field(..., description="The optimized prompt string.")
    cost: float = Field(..., description="The cost of the optimization run.")
    tokens: int = Field(..., description="The number of tokens used in the optimization run.")
    latency: float = Field(..., description="The latency of the optimization run in seconds.")
    status: str = Field("success", description="Status of the optimization run (success/failure).")
    error_message: Optional[str] = Field(None, description="Error message if the optimization failed.")

class RunSummary(BaseModel):
    run_id: str = Field(..., description="Unique identifier for the optimization run.")
    timestamp: str = Field(..., description="Timestamp of the run.")
    original_prompt_snippet: str = Field(..., description="A snippet of the original prompt.")
    cost: float = Field(..., description="Cost of the run.")
    tokens: int = Field(..., description="Tokens used in the run.")
    latency: float = Field(..., description="Latency of the run in seconds.")
    status: str = Field(..., description="Status of the run (success/failure).")

class ErrorResponse(BaseModel):
    detail: str = Field(..., description="Detailed error message.") 