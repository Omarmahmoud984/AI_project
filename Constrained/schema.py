from typing import Optional, Literal, Dict, Any
from pydantic import BaseModel, Field


class ToolCall(BaseModel):
    tool: Literal[
        "check_doctor_availability",
        "get_doctor_schedule",
        "list_all_doctors",
        "route_department",
    ]
    args: Dict[str, Any] = Field(default_factory=dict)


class AgentStep(BaseModel):
    thought: str
    action: Optional[ToolCall] = None
    final_answer: Optional[str] = None
    escalate: bool = False