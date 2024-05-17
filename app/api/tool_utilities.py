import json
import os
from services.logger import setup_logger
from services.tool_registry import ToolFile
from fastapi import HTTPException

logger = setup_logger(__name__)

def load_config():
    config_path = os.path.join(os.path.dirname(__file__), "tools_config.json")
    with open(config_path, 'r') as f:
        return json.load(f)

tools_config = load_config()

def get_executor_by_name(module_path):
    try:
        module = __import__(module_path, fromlist=['executor'])
        return getattr(module, 'executor')
    except Exception as e:
        logger.error(f"Failed to import executor from {module_path}: {str(e)}")
        raise ImportError(f"Failed to import module from {module_path}: {str(e)}")

def load_tool_metadata(tool_id):
    logger.debug(f"Loading tool metadata for tool_id: {tool_id}")
    tool_config = tools_config.get(str(tool_id))
    if not tool_config:
        logger.error(f"No tool configuration found for tool_id: {tool_id}")
        raise HTTPException(status_code=404, detail="Tool configuration not found")
    
    # The path to the module needs to be split and only the directory path should be used.
    module_dir_path = '/'.join(tool_config['path'].split('.')[:-1])  # This removes the last segment (core)
    file_path = os.path.join(os.getcwd(), module_dir_path, tool_config['metadata_file'])
    logger.debug(f"Checking metadata file at: {file_path}")
    
    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        logger.error(f"Metadata file missing or empty at: {file_path}")
        raise HTTPException(status_code=404, detail="Tool metadata not found")
    
    with open(file_path, 'r') as f:
        metadata = json.load(f)
    logger.debug(f"Loaded metadata: {metadata}")
    return metadata

def prepare_input_data(request_data):
    inputs = {input.name: input.value for input in request_data.inputs}
    files = next((input.value for input in request_data.inputs if input.name == "files"), None)
    if files:
        inputs['files'] = [ToolFile(**file_object) for file_object in files]
    return inputs

def execute_tool(tool_id, request_inputs_dict):
    try:
        tool_config = tools_config.get(str(tool_id))
        if not tool_config:
            raise HTTPException(status_code=404, detail="Tool executable not found")
        execute_function = get_executor_by_name(tool_config['path'])
        request_inputs_dict['verbose'] = True
        return execute_function(**request_inputs_dict)
    except ImportError as e:
        logger.error(f"Failed to execute tool due to import error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to execute tool: {str(e)}")
    except Exception as e:
        logger.error(f"Encountered error in executing tool: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))