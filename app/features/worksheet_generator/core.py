from app.services.tool_registry import ToolQuestionType
from services.logger import setup_logger
from app.features.worksheet_generator.tools import WorksheetGenerator
from app.api.error_utilities import LoaderError, ToolExecutorError

logger = setup_logger()

def executor(grade_level : int, topic: str, difficulty_level: str, question_types: list[ToolQuestionType], verbose=False):
    
    try:
        if verbose: logger.debug(f"grade_level: {grade_level}, topic: {topic}, difficulty_level: {difficulty_level}, question_types: {question_types}")
        
        params = {"grade_level": grade_level, "topic": topic, "difficulty_level": difficulty_level, "question_types": question_types, "verbose": verbose}

        # Create and return the questions for the worksheet 
        output = WorksheetGenerator(**params).create_worksheet()
    
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