from pydantic import BaseModel, ValidationError, field_validator
from typing import List, Union, Any

class ToolInput(BaseModel):
    name: str
    value: Any
    
# Base model for all tools
class BaseTool(BaseModel):
    tool_id: int  # Unique identifier for each tool,
    inputs: List[ToolInput]

def validate_inputs(request_data: dict, validate_data: list) -> bool:
    validate_inputs = {input_item['name']: input_item['type'] for input_item in validate_data}
    
    # Check for missing inputs, but skip 'file' types
    for validate_input_name, input_type in validate_inputs.items():
        if input_type == "file":
            continue  # Skip file inputs during missing input check
        if validate_input_name not in request_data:
            print(f"Missing input: `{validate_input_name}`")
            return False
    
    # Validate each input in request data against validate definitions, but skip 'file' types
    for input_name, input_value in request_data.items():
        # Skip validation for extra inputs not defined in validate and for 'file' types
        if input_name not in validate_inputs or validate_inputs[input_name] == "file":
            continue
        
        expected_type = validate_inputs[input_name]
        if expected_type == 'text' and not isinstance(input_value, str):
            print(f"Input `{input_name}` must be a string")
            return False
        elif expected_type == 'number' and not isinstance(input_value, (int, float)):
            print(f"Input `{input_name}` must be a number")
            return False
    
    return True

