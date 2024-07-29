from app.services.logger import setup_logger
from dotenv import load_dotenv
import os
from pathlib import Path
from app.features.syllabus_generator.tools import Syllabus_generator

logger = setup_logger()

env_path = Path(__file__).resolve().parents[2] / '.env'
load_dotenv(dotenv_path=env_path)

API_KEY = os.getenv('API_KEY')
SEARCH_ENGINE_ID = os.getenv('SEARCH_ENGINE_ID')

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "local-auth.json"

def executor(grade: str, subject: str, Syllabus_type:str) -> str:
    """
    Executes the tool's functionality.
    
    Args:
        grade_level (int): The grade level for the content.
        topic (str): The topic of interest.
        context (str): Additional context or information.

    Returns:
        str: The result or output of the tool's functionality.
    """
    try:
        Generator = Syllabus_generator(grade,subject,Syllabus_type,API_KEY,SEARCH_ENGINE_ID,"app/features/syllabus_generator")

        response = Generator.run(verbose=True)
        
        return response
        # Example of tool's logic (this should be detailed and explicit before abstraction)
        #logger.error(f"Executing with grade_level={grade_level}, topic={topic}, context={context}")
        
        # Here you would define the core functionality
        #Prompt
        #prompt_template = f"Create content for grade {grade_level} on {topic}. Context: {context}"
        # Call the Gemini API to generate a response
        #response = generate_response(prompt_template) 
        
        #logger.error(f"Execution successful: {response}")

    
    except Exception as e:
        error_message = f"Error in executor: {e}"
        logger.error(error_message)
        raise ValueError(error_message)
    
