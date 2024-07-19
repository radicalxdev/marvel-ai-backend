# This is code from quizbuilder - repurpose for syllabus generator
from services.logger import setup_logger
from gemini_api_client import generate_response

logger = setup_logger()

def executor(grade_level: int, topic: str, context: str) -> str:
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
        # Example of tool's logic (this should be detailed and explicit before abstraction)
        logger.error(f"Executing with grade_level={grade_level}, topic={topic}, context={context}")
        
        # Here you would define the core functionality
        #Prompt
        prompt_template = f"Create content for grade {grade_level} on {topic}. Context: {context}"
        # Call the Gemini API to generate a response
        response = generate_response(prompt_template) 
        
        logger.error(f"Execution successful: {result}")

    except LoaderError as e:
        error_message = e
        logger.error(f"Error in RAGPipeline -> {error_message}")
        raise ToolExecutorError(error_message)
    
    except Exception as e:
        error_message = f"Error in executor: {e}"
        logger.error(error_message)
        raise ValueError(error_message)
    
    return response
