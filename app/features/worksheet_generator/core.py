from services.logger import setup_logger
#from app.features.worksheet_generator.tools import RAGpipeline
from app.features.worksheet_generator.tools import create_question_builder
from app.api.error_utilities import LoaderError, ToolExecutorError

logger = setup_logger()

def executor(grade_level : int, topic: str, question_type: str, num_questions:int, verbose=False):
    
    try:
        if verbose: logger.debug(f"Files: {grade_level}, topic: {topic}, question_type: {question_type}, num_questions: {num_questions}")
        
        # Create and return the questions for the worksheet 
        params = {"grade_level": grade_level, "topic": topic, "verbose": verbose}
        output = create_question_builder(question_type, **params).create_questions(num_questions)
    
    # Try-Except blocks on custom defined exceptions to provide better logging
    
    except LoaderError as e:
        error_message = e
        logger.error(f"Error in RAGPipeline -> {error_message}")
        raise ToolExecutorError(error_message)
    
    # These help differentiate user-input errors and internal errors. Use 4XX and 5XX status respectively.
    except Exception as e:
        error_message = f"Error in executor: {e}"
        logger.error(error_message)
        raise ValueError(error_message)
    
    return output