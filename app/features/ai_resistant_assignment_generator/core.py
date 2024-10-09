from app.features.ai_resistant_assignment_generator.document_loaders import get_docs
from app.features.ai_resistant_assignment_generator.tools import AIResistantAssignmentGenerator
from app.services.schemas import AIResistantArgs
from app.services.logger import setup_logger
from app.api.error_utilities import LoaderError, ToolExecutorError

logger = setup_logger()

def executor(ai_resistant_args: AIResistantArgs, verbose=False):
    
    try:
        if verbose: print(f"Args.: {ai_resistant_args}")

        logger.info(f"Generating docs. from {ai_resistant_args.file_type}")

        docs = get_docs(ai_resistant_args.file_url, ai_resistant_args.file_type, True)

        output = AIResistantAssignmentGenerator(args=ai_resistant_args, verbose=verbose).create_assignments(docs)

        logger.info(f"AI-Resistant Assignments generated successfully")

    except LoaderError as e:
        error_message = e
        logger.error(f"Error in AI Resistant Assignment Generator Pipeline -> {error_message}")
        raise ToolExecutorError(error_message)
    
    except Exception as e:
        error_message = f"Error in executor: {e}"
        logger.error(error_message)
        raise ValueError(error_message)
    
    return output

