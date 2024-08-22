from app.services.tool_registry import ToolFile
from app.services.logger import setup_logger
from app.features.syllabus.tools import SyllabusBuilder
from app.api.error_utilities import LoaderError, ToolExecutorError

logger = setup_logger()

def executor(grade_level: str, course_title: str, course_description: str, objectives_topics: str = None, required_materials: str = None, num_weeks: str = None, course_outline: str = None, grading_policy: str = None, class_policy: str = None, customization: str = None, verbose=False):
    attributes = {}
    attributes['grade_level'] = grade_level
    attributes['course_title'] = course_title
    attributes['course_description'] = course_description
    attributes['objectives_topics'] = objectives_topics
    attributes['required_materials'] = required_materials
    attributes['num_weeks'] = num_weeks
    attributes['course_outline'] = course_outline
    attributes['grading_policy'] = grading_policy
    attributes['class_policy'] = class_policy
    attributes['customization'] = customization
    
    try:
        output = SyllabusBuilder(attributes, verbose = verbose).create_syllabus()
    
    except Exception as e:
        error_message = f"Error in executor: {e}"
        logger.error(error_message)
        raise ValueError(error_message)
    
    return output

