from app.features.syllabus_generator.tools import SyllabusGenerator
from app.api.error_utilities import ToolExecutorError,ErrorResponse,InputValidationError
from app.services.logger import setup_logger
import os
from typing import Optional

logger = setup_logger()

def executor(grade_level: str, subject: str,additional_objectives: Optional[str] = None ,
             additional_materials: Optional[str] = None, additional_gradingpolicy: Optional[str] = None,
             additional_classpolicy: Optional[str] = None, custom_courseoutline: Optional[str] = None, verbose = True):
    try:
        additional_objectives = additional_objectives if additional_objectives else None
        additional_materials = additional_materials if additional_materials else None
        additional_gradingpolicy = additional_gradingpolicy if additional_gradingpolicy else None
        additional_classpolicy = additional_classpolicy if additional_classpolicy else None
        custom_courseoutline = custom_courseoutline if custom_courseoutline else None

        generator = SyllabusGenerator(grade_level, subject,additional_objectives,
                                      additional_materials,additional_gradingpolicy,
                                      additional_classpolicy,custom_courseoutline)
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
