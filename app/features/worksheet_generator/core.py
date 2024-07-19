from app.services.logger import setup_logger
from app.services.tool_registry import WorksheetQuestionModel
from app.features.worksheet_generator.tools import generate_course_type, worksheet_generator
from app.features.worksheet_generator.document_loaders import get_docs

logger = setup_logger()

def executor(topic: str, grade_level: str, worksheet_list: list[WorksheetQuestionModel], file_type: str, file_url: str, verbose=True):
    
    course_type = generate_course_type(topic, verbose)['course_type']

    if verbose:
        logger.info(f"File URL loaded: {file_url}")

    docs = get_docs(file_url, file_type, verbose)
    worksheet = worksheet_generator(course_type=course_type, grade_level=grade_level, worksheet_list=worksheet_list, documents=docs, verbose=verbose)
    print(worksheet)
    return worksheet