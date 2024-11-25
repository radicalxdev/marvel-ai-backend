from app.services.logger import setup_logger
from app.api.error_utilities import LoaderError, ToolExecutorError
from app.services.schemas import RubricGeneratorArgs
from app.features.rubric_generator.document_loaders import get_docs
from app.features.rubric_generator.tools import RubricGenerator

logger = setup_logger()

def executor(standard: str,
             point_scale: int,
             grade_level: str,
             assignment_desc: str,
             additional_customization: str,
             file_type: str,
             file_url: str,
             lang: str,
             verbose=False):
    try:
        if verbose: 
            logger.info(f"File URL loaded: {file_url}")

        logger.info(f"Generating docs from {file_type}")

        docs = get_docs(file_url, file_type, verbose=True)
        
        # Create and return the Rubric
        rubric_generator_args = RubricGeneratorArgs(
            standard=standard,
            point_scale=point_scale,
            grade_level=grade_level,
            assignment_desc=assignment_desc,
            additional_customization=additional_customization,
            file_type=file_type,
            file_url=file_url,
            lang=lang
        )
        
        output = RubricGenerator(args=rubric_generator_args, verbose=verbose).create_rubric(docs)

        print(output)
        
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