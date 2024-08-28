from app.services.logger import setup_logger
from app.features.worksheet_generator.tools import generate_course_type, worksheet_generator
from app.features.worksheet_generator.document_loaders import get_docs
from app.services.schemas import WorksheetGeneratorArgs

logger = setup_logger()

def executor(worksheet_generator_args:WorksheetGeneratorArgs, verbose=True):

    
    course_type = generate_course_type(worksheet_generator_args.topic, verbose)['course_type']

    if verbose:
        logger.info(f"Course Type: {course_type} [{worksheet_generator_args.lang}]")
        logger.info(f"File URL loaded: {worksheet_generator_args.file_url}")

    docs = get_docs(worksheet_generator_args.file_url, worksheet_generator_args.file_type, verbose)
    worksheet = worksheet_generator(course_type=course_type, 
                                    grade_level=worksheet_generator_args.grade_level, 
                                    worksheet_list=worksheet_generator_args.worksheet_list, 
                                    documents=docs, 
                                    lang=worksheet_generator_args.lang, 
                                    verbose=verbose)

    print(worksheet)
    return worksheet