from pydantic import BaseModel

class AgentState(BaseModel):
    acceptance_criteria: str = "Exactly text match."
    user_message: str = ""
    expected_output: str = ""
    system_message: str = ""
    output: str = ""
    suggestions: str = ""
    accepted: bool = False
    analysis: str = ""
    best_output: str = ""
    best_system_message: str = ""
    best_output_age: int = 0
    max_output_age: int = 3
    iteration: int = 0
    max_iterations: int = 10 