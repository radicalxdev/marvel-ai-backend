from app.features.quizzify.document_loaders import get_docs
from app.services.logger import setup_logger
from app.features.quizzify.tools import QuizBuilder
from app.api.error_utilities import LoaderError, ToolExecutorError
from app.services.schemas import QuizzifyArgs

logger = setup_logger()

def executor(quizzify_args: QuizzifyArgs, verbose=True):
    
    try:
        if verbose:
            logger.info(f"File URL loaded: {quizzify_args.file_url}")

        docs = get_docs(quizzify_args.file_url, quizzify_args.file_type, verbose)
    
        output = QuizBuilder(quizzify_args.topic, quizzify_args.lang, verbose=verbose).create_questions(docs, quizzify_args.n_questions)
    
    except LoaderError as e:
        error_message = e
        logger.error(f"Error in RAGPipeline -> {error_message}")
        raise ToolExecutorError(error_message)
    
    except Exception as e:
        error_message = f"Error in executor: {e}"
        logger.error(error_message)
        raise ValueError(error_message)
    
    return output

