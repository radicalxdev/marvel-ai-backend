from app.services.tool_registry import ToolFile
from app.services.logger import setup_logger
from app.features.quizzify.tools import RAGpipeline
from app.features.quizzify.tools import QuizBuilder
from app.api.error_utilities import LoaderError, ToolExecutorError

logger = setup_logger()


def executor(files, topic: str, num_questions: int, verbose=False):
    try:
        if verbose: logger.debug(f"Files: {files}")

        # Instantiate RAG pipeline with default values
        pipeline = RAGpipeline(verbose=verbose)

        pipeline.compile()

        # Process the uploaded files
        db = pipeline(files)

        # Create and return the quiz questions
        output = QuizBuilder(db, topic, verbose=verbose).create_questions(num_questions)

    except LoaderError as e:
        error_message = e
        logger.error(f"Error in RAGPipeline -> {error_message}")
        raise ToolExecutorError(error_message)

    except Exception as e:
        error_message = f"Error in executor: {e}"
        logger.error(error_message)
        raise ValueError(error_message)

    return output

