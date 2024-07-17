from app.services.logger import setup_logger
from app.services.tool_registry import WorksheetQuestionModel
from app.features.worksheet_generator.tools import generate_course_type

logger = setup_logger()

def executor(topic: str, grade_level: str, worksheet_list: list[WorksheetQuestionModel], file_type: str, file_url: str, verbose=True):
    print(topic)    
    print(grade_level)
    print(worksheet_list)
    print(file_type)
    print(file_url)

    return generate_course_type(topic, verbose)
