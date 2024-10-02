from services.logger import setup_logger
from app.api.error_utilities import LoaderError, ToolExecutorError
from app.services.schemas import RubricGeneratorArgs
from app.features.rubric_generator.document_loaders import get_docs

logger = setup_logger()

def executor(rubric_generator_args: RubricGeneratorArgs, verbose=False):
    print("INSIDE---def executor(rubric_generator_args) ")
    try:
        if verbose: 
            print(f"Args.: {rubric_generator_args}")
            logger.info(f"File URL loaded: {rubric_generator_args.file_url}")

        logger.info(f"Generating docs from {rubric_generator_args.file_type}")

        docs = get_docs(rubric_generator_args.file_url, rubric_generator_args.file_type, verbose=True)
        
        # Create and return the quiz questions
        #output = RubricGenerator(args=rubric_generator_args, verbose=verbose).create_rubric(docs)
        output = docs

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