from app.features.syllabus_generator.tools import SyllabusGenerator
from app.api.error_utilities import ToolExecutorError,ErrorResponse,InputValidationError
from app.services.logger import setup_logger
import os
from typing import Optional

logger = setup_logger()

def executor(grade_level: str, subject: str, num_weeks: int,
             start_date: Optional[str] = None, additional_objectives: Optional[str] = None ,
             additional_materials: Optional[str] = None, additional_grading_policy: Optional[str] = None,
             additional_class_policy: Optional[str] = None, custom_course_outline: Optional[str] = None,verbose = True):
    try:
        generator = SyllabusGenerator(grade_level, subject,num_weeks,start_date, 
                                    additional_objectives, additional_materials,additional_grading_policy,
                                    additional_class_policy,custom_course_outline)
        
        result = generator.generate()
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