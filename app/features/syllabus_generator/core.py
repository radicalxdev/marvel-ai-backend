from app.features.syllabus_generator.tools import SyllabusGenerator
from app.api.error_utilities import ToolExecutorError,ErrorResponse,InputValidationError
from app.services.logger import setup_logger
import os

logger = setup_logger()

def executor(grade_level: str, subject: str, verbose: bool = True):
    try:
        generator = SyllabusGenerator(grade_level, subject)
        result = generator.compile()
        if verbose:
            print(result)
        return result
    except ToolExecutorError as e:
        logger.error(f"Execution error: {e}")
        if verbose:
            print(f"An error occurred: {e}")
        return ErrorResponse(status=500, message=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        if verbose:
            print(f"An unexpected error occurred: {e}")
        return ErrorResponse(status=500, message="An unexpected error occurred.")
