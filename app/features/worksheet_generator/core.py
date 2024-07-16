import logging
from typing import List
from app.api.error_utilities import ToolExecutorError, LoaderError
from app.services.tool_registry import ToolFile
import requests
from app.features.worksheet_generator.tools import RAGpipeline, QuizBuilder


logger = logging.getLogger(__name__)

def executor(files: List[ToolFile], topic: str, num_questions: int, grade_level: str, question_type: str, context: str, verbose: bool = False):
    # Validate inputs
    if not files:
        error_message = "No files provided for processing"
        logger.error(error_message)
        raise ToolExecutorError(error_message)

    if not topic:
        error_message = "No topic provided"
        logger.error(error_message)
        raise ToolExecutorError(error_message)

    if num_questions <= 0 or num_questions > 10:
        error_message = "Number of questions must be between 1 and 10"
        logger.error(error_message)
        raise ToolExecutorError(error_message)

    if not grade_level:
        error_message = "No grade level provided"
        logger.error(error_message)
        raise ToolExecutorError(error_message)

    if not question_type:
        error_message = "No question type provided"
        logger.error(error_message)
        raise ToolExecutorError(error_message)

    if not context:
        error_message = "No context provided"
        logger.error(error_message)
        raise ToolExecutorError(error_message)

    try:
        if verbose:
            logger.debug(f"Files: {files}")
            logger.debug(f"Topic: {topic}, Grade Level: {grade_level}, Question Type: {question_type}, Context: {context}, Number of Questions: {num_questions}")

        pipeline = RAGpipeline(verbose=verbose)
        pipeline.compile()

        db = pipeline(files)

        if verbose:
            logger.debug(f"Database after processing files: {db}")

        quiz_builder = QuizBuilder(db, topic, verbose=verbose)
        output = quiz_builder.create_questions(num_questions)

        if not output:
            error_message = "No questions generated"
            logger.error(error_message)
            raise ToolExecutorError(error_message)

        return output

    except LoaderError as e:
        error_message = str(e)
        logger.error(f"Error in RAGPipeline -> {error_message}")
        raise ToolExecutorError(error_message)

    except requests.exceptions.RequestException as e:
        error_message = f"Network error occurred: {e}"  # Additional error handling for requests exceptions
        logger.error(error_message)
        raise ToolExecutorError(error_message)

    except pypdf.errors.PdfReadError as e:
        error_message = f"PDF read error occurred: {e}"  # Additional error handling for PDF read errors
        logger.error(error_message)
        raise ToolExecutorError(error_message)

    except Exception as e:
        error_message = f"Unexpected error in executor: {e}"  # More specific exception handling
        logger.error(error_message)
        raise ValueError(error_message)
