# This is code from quizbuilder - repurpose for syllabus generator
from app.services.logger import setup_logger
from dotenv import load_dotenv
import os
from pathlib import Path
# from gemini_api_client import generate_response
from tools import get_table_from_link,course_objectives,course_description,course_outline,grading_policy,rules_policies,study_materials,final_output
logger = setup_logger()

env_path = Path(__file__).resolve().parents[2] / '.env'

# Load the .env file
load_dotenv(dotenv_path=env_path)

#Retrieve the value of the environment variable
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
SEARCH_ENGINE_ID = os.getenv('SEARCH_ENGINE_ID')

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "local-auth.json"

def executor(grade_level: str, topic: str, context: str) -> str:
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
        web_search = get_table_from_link(grade_level,topic,GOOGLE_API_KEY,SEARCH_ENGINE_ID)
        
        description = course_description(grade_level,topic,custom_info=context)

        objectives = course_objectives(grade_level,topic,description,custom_info=context)

        outline = course_outline(grade_level,topic,description,objectives,web_search,custom_info=context) 

        grading = grading_policy(grade_level,topic,outline,custom_info=context)

        class_rules = rules_policies(grade_level,topic,outline,custom_info=context)

        materials = study_materials(grade_level,topic,outline,custom_info=context)

        response = final_output(description,objectives,outline,grading,class_rules,materials)
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
    
    return response
