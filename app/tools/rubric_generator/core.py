from app.services.logger import setup_logger
from app.api.error_utilities import LoaderError, ToolExecutorError
from app.services.schemas import RubricGeneratorArgs
from app.utils.document_loaders import get_docs
from app.tools.rubric_generator.tools import RubricGenerator

logger = setup_logger()

def executor(grade_level: str,
             point_scale: int,
             objectives: str,
             assignment_desc: str,
             objectives_file_url: str,
             objectives_file_type: str,
             assignment_description_file_url: str,
             assignment_description_file_type: str,
             lang: str,
             verbose=False):
    try:
        if objectives_file_type: 
            logger.info(f"Generating docs from {objectives_file_type}")
        if assignment_description_file_type: 
            logger.info(f"Generating docs from {assignment_description_file_type}")

        docs = None

        def fetch_docs(file_url, file_type):
            return get_docs(file_url, file_type, True) if file_url and file_type else None

        objectives_docs = fetch_docs(objectives_file_url, objectives_file_type)
        assignment_desc_comments_docs = fetch_docs(assignment_description_file_url, assignment_description_file_type)

        docs = (
            objectives_docs + assignment_desc_comments_docs
            if objectives_docs and assignment_desc_comments_docs
            else objectives_docs or assignment_desc_comments_docs
        )
        
        # Create and return the Rubric
        rubric_generator_args = RubricGeneratorArgs(
            grade_level=grade_level,
            point_scale=point_scale,
            objectives=objectives,
            assignment_desc=assignment_desc,
            objectives_file_url=objectives_file_url,
            objectives_file_type=objectives_file_type,
            assignment_description_file_url=assignment_description_file_url,
            assignment_description_file_type=assignment_description_file_type,
            lang=lang
        )
        
        output = RubricGenerator(args=rubric_generator_args, verbose=verbose).create_rubric(docs)

        logger.info(f"Rubric generated successfully")
    
    except LoaderError as e:
        error_message = e
        logger.error(f"Error in Rubric Genarator Pipeline -> {error_message}")
        raise ToolExecutorError(error_message)
    
    except Exception as e:
        error_message = f"Error in executor: {e}"
        logger.error(error_message)
        raise ValueError(error_message)
    
    return output