from typing import Any, List
from pydantic import BaseModel

class ToolInput(BaseModel):
    name: str
    value: Any

class AssistantInputs(BaseModel):
    assistant_group: str
    assistant_name: str
    inputs: List[ToolInput]