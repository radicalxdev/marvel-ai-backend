from app.services.logger import setup_logger
from typing import List
from app.api.error_utilities import ToolExecutorError, LoaderError
from app.services.tool_registry import ToolFile
from app.features.worksheet_generator.tools import RAGpipeline, QuizBuilder

logger = setup_logger(__name__)

def executor(files: List[ToolFile], topic: str, num_questions: int, grade_level: str, question_type: str, context: str, verbose: bool = False):
    if not files:
        error_message = "No files provided for processing"
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

    except LoaderError as e:
        error_message = str(e)
        logger.error(f"Error in RAGPipeline -> {error_message}")
        raise ToolExecutorError(error_message)

    except Exception as e:
        error_message = f"Error in executor: {e}"
        logger.error(error_message)
        raise ValueError(error_message)

    return output