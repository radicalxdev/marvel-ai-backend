from pydantic import BaseModel, ValidationError, field_validator
from typing import List, Union, Any

class ToolInput(BaseModel):
    name: str
    value: Any
    
# Base model for all tools
class BaseTool(BaseModel):
    tool_id: int  # Unique identifier for each tool,
    inputs: List[ToolInput]

def validate_inputs(request_data: dict, firestore_data: list):
    firestore_inputs = {input_item['name']: input_item['type'] for input_item in firestore_data}
    
    # Check for missing inputs
    for firestore_input_name in firestore_inputs.keys():
        if firestore_input_name not in request_data:
            print(f"Missing input: `{firestore_input_name}`")
            return False
    
    # Validate each input in request data against Firestore definitions
    for input_name, input_value in request_data.items():
        # Skip validation for extra inputs not defined in Firestore
        if input_name not in firestore_inputs:
            continue
        
        expected_type = firestore_inputs[input_name]
        if expected_type == 'text' and not isinstance(input_value, str):
            print(f"Input `{input_name}` must be a string")
            return False
        elif expected_type == 'number' and not isinstance(input_value, (int, float)):
            print(f"Input `{input_name}` must be a number")
            return False
    
    return True
