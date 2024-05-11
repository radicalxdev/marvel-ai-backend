from pydantic import BaseModel, ValidationError, field_validator
from typing import List, Union, Any

#########################
# Base model for all tools
class BaseTool(BaseModel):
    tool_id: int  # Unique identifier for each tool
    
class ToolInput(BaseModel):
    name: str
    value: Any

# Tool 0: Topic and Questions
class Quizzify(BaseTool):
    @field_validator('inputs', check_fields=False)
    def check_inputs(cls, v):
        if not any(item['name'] == 'topic' for item in v):
            raise ValueError("Missing 'topic' input")
        if not any(item['name'] == 'num_questions' for item in v):
            raise ValueError("Missing 'num_questions' input")
        return v

# Tool 1: YouTube and Cards
class Dynamo(BaseTool):
    @field_validator('inputs', check_fields=False)
    def validate_inputs(cls, v):
        youtube_url = None
        num_cards = None
        for item in v:
            if item.name == "youtube_url":
                youtube_url = item.value
            elif item.name == "num_cards":
                num_cards = item.value
        
        if youtube_url is None or num_cards is None:
            raise ValueError("URL and number of cards must be provided.")
        return v

#########################

def validate_tool(data: dict) -> BaseTool:
    tool_type = data.get('tool_id')
    tool_classes = {
        0: Quizzify,
        1: Dynamo,
    }
    tool_class = tool_classes.get(tool_type)
    
    if not tool_class:
        raise ValueError(f"Invalid tool_id {tool_type}")
    
    try:
        validated_tool = tool_class(**data)
    except ValueError as e:
        print(e.json())
        raise ValueError("Validation failed for the tool data.")
    
    return validated_tool