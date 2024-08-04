from app.services.logger import setup_logger
from dotenv import load_dotenv
import os
from typing import List
from pathlib import Path
from app.features.syllabus_generator.tools import Syllabus_generator
from app.services.tool_registry import ToolInput
from typing import Any, List, Dict

logger = setup_logger(__name__)


env_path = Path(__file__).resolve().parents[2] / '.env'
load_dotenv(dotenv_path=env_path)

API_KEY = os.getenv('API_KEY')
SEARCH_ENGINE_ID = os.getenv('SEARCH_ENGINE_ID')

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "local-auth.json"

def executor(tool_id: int, inputs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Executes the tool's functionality and returns a dictionary.
    
    Args:
        tool_id (int): The ID of the tool to use.
        inputs (List[ToolInput]): The list of inputs for the tool.

    Returns:
        dict: A dictionary containing tool-specific details.
    """
    try:
        
        input_mapping = {input_item['name']: input_item['value'] for input_item in inputs}
        
        if tool_id == 1:
            # Assume tool_id 1 corresponds to generating a syllabus
            grade = input_mapping.get("grade")
            subject = input_mapping.get("subject")
            syllabus_type = input_mapping.get("Syllabus_type")
            instructions = input_mapping.get('instructions')
            if instructions is None:
                instructions = 'None'

            # instruction is an optional parameter
            if not grade or not subject or not syllabus_type:
                raise ValueError("Missing required parameters: 'grade', 'subject', or 'Syllabus_type'")
            
            # Execute the syllabus generation logic (using a mockup function for illustration)
            Generator = Syllabus_generator(grade=grade,
                                           subject=subject, 
                                           Syllabus_type=syllabus_type, 
                                           instructions=instructions,
                                           API_KEY=API_KEY, 
                                           SEARCH_ENGINE_ID=SEARCH_ENGINE_ID, 
                                           path="app/features/syllabus_generator/")

            result = Generator.run(verbose=False)
        
        else:
            raise ValueError(f"Unsupported tool_id: {tool_id}")
        
        
        return result
    
    except Exception as e:
        error_message = f"Error in executor: {e}"
        logger.error(error_message)
        raise ValueError(error_message)

