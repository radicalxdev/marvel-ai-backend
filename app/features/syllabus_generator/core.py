from app.features.quizzify.tools import RAGpipeline
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders.text import TextLoader
from app.services.tool_registry import ToolFile
from services.logger import setup_logger
from app.features.syllabus_generator.tools import SyllabusBuilder
from app.api.error_utilities import LoaderError, ToolExecutorError
import traceback

logger = setup_logger()


def executor(subject: str, grade_level: str, verbose=True, **kwargs):
    try:
        if verbose:
            logger.debug(f"Subject: {subject}, grade_level: {grade_level}")

        # Create and return the quiz questions
        output = SyllabusBuilder(
            subject, grade_level, verbose=verbose
        ).create_syllabus()
        print(output)

    except LoaderError as e:
        error_message = e
        logger.error(f"Error in RAGPipeline -> {error_message}")
        raise ToolExecutorError(error_message.message)

    except Exception as e:
        print(traceback.format_exc())
        error_message = f"Error in executor: {e}"
        logger.error(error_message)
        raise ValueError(error_message)

    return output


if __name__ == "__main__":
    executor(subject="Multiplication", grade_level="K12")
