import json
import os
from typing import Any, Dict, List

from fastapi import HTTPException
from app.api.error_utilities import InputValidationError
from app.services.logger import setup_logger

logger = setup_logger(__name__)

def load_config():
    config_path = os.path.join(os.path.dirname(__file__), "assistants_config.json")
    with open(config_path, 'r') as f:
        return json.load(f)

assistants_config = load_config()

def get_executor_by_name(module_path):
    try:
        module = __import__('app.'+module_path, fromlist=['executor'])
        return getattr(module, 'executor')
    except Exception as e:
        logger.error(f"Failed to import executor from {module_path}: {str(e)}")
        raise ImportError(f"Failed to import module from {module_path}: {str(e)}")
    
def load_assistant_metadata(assistant_group, assistant_name):
    logger.debug(f"Loading Assistant metadata for Assistant Group: {assistant_group} - Assistant Name: {assistant_name}")
    assistant_group = assistants_config.get(str(assistant_group))
    assistant_config = assistant_group.get(str(assistant_name))
    
    if not assistant_config:
        logger.error(f"No Assistant configuration found for Assistant Group: {assistant_group} - Assistant Name: {assistant_name}")
        raise HTTPException(status_code=404, detail="Assistant configuration not found")
    
    # Ensure the base path is relative to the current file's directory
    base_dir = os.path.dirname(os.path.abspath(__file__))
    logger.debug(f"Base directory: {base_dir}")
    
    # Construct the directory path
    module_dir_path = os.path.join(base_dir, '../..', *assistant_config['path'].split('.')[:-1])  # Go one level up and then to the path
    module_dir_path = os.path.abspath(module_dir_path)  # Get absolute path
    logger.debug(f"Module directory path: {module_dir_path}")
    
    file_path = os.path.join(module_dir_path, assistant_config['metadata_file'])
    logger.debug(f"Checking metadata file at: {file_path}")
    
    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        logger.error(f"Metadata file missing or empty at: {file_path}")
        raise HTTPException(status_code=404, detail="Assistant metadata not found")
    
    with open(file_path, 'r') as f:
        metadata = json.load(f)
        
    logger.debug(f"Loaded metadata: {metadata}")
    return metadata

def prepare_input_data(input_data) -> Dict[str, Any]:
    inputs = {input.name: input.value for input in input_data}
    return inputs

def check_missing_inputs(request_data: Dict[str, Any], validate_inputs: Dict[str, str]):
    for validate_input_name in validate_inputs:
        if validate_input_name not in request_data:
            error_message = f"Missing input: `{validate_input_name}`"
            logger.error(error_message)
            raise InputValidationError(error_message)

def raise_type_error(input_name: str, input_value: Any, expected_type: str):
    error_message = f"Input `{input_name}` must be a {expected_type} but got {type(input_value)}"
    logger.error(error_message)
    raise InputValidationError(error_message)

def validate_input_type(input_name: str, input_value: Any, expected_type: str):
    if expected_type == 'text' and not isinstance(input_value, str):
        raise_type_error(input_name, input_value, "string")
    elif expected_type == 'number' and not isinstance(input_value, (int, float)):
        raise_type_error(input_name, input_value, "number")

def validate_inputs(request_data: Dict[str, Any], validate_data: List[Dict[str, str]]) -> bool:
    validate_inputs = {input_item['name']: input_item['type'] for input_item in validate_data}
    
    # Check for missing inputs
    check_missing_inputs(request_data, validate_inputs)

    # Validate each input in request data against validate definitions
    for input_name, input_value in request_data.items():
        if input_name not in validate_inputs:
            continue  # Skip validation for extra inputs not defined in validate_inputs

        expected_type = validate_inputs[input_name]
        validate_input_type(input_name, input_value, expected_type)

    return True

def finalize_inputs_assistants(input_data, validate_data: List[Dict[str, str]]) -> Dict[str, Any]:
    inputs = prepare_input_data(input_data)
    validate_inputs(inputs, validate_data)
    return inputs

def execute_assistant(assistant_group, assistant_name, request_inputs_dict):
    try:
        assistant_group = assistants_config.get(str(assistant_group))
        assistant_config = assistant_group.get(str(assistant_name))     

        if not assistant_config:
            raise HTTPException(status_code=404, detail="Assistant executable not found")
        
        execute_function = get_executor_by_name(assistant_config['path'])
        
        return execute_function(**request_inputs_dict)
    
    except ImportError as e:
        logger.error(f"Failed to execute assistant due to import error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    
    except Exception as e:
        logger.error(f"Encountered error in executing assistant: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))