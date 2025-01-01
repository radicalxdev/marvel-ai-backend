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
    

def execute_assistant(assistant_group, assistant_name, user_info, messages):
    try:
        assistant_group = assistants_config.get(str(assistant_group))
        assistant_config = assistant_group.get(str(assistant_name))     

        if not assistant_config:
            raise HTTPException(status_code=404, detail="Assistant executable not found")
        
        execute_function = get_executor_by_name(assistant_config['path'])
        
        return execute_function(user_info, messages)
    
    except ImportError as e:
        logger.error(f"Failed to execute assistant due to import error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    
    except Exception as e:
        logger.error(f"Encountered error in executing assistant: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))