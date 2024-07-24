import traceback

from app.api.error_utilities import LoaderError, ToolExecutorError
from app.features.quizzify.tools import RAGpipeline
from app.features.syllabus_generator.tools import SyllabusBuilder
from app.services.tool_registry import ToolFile
from langchain_community.document_loaders.text import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from services.logger import setup_logger

logger = setup_logger()


def executor(
    subject: str, grade_level: str, course_overview: str, verbose: bool = True, **kwargs
) -> dict:
    """Execute the syllabus generation process."""
    try:
        if verbose:
            logger.debug(
                f"Subject: {subject}, Grade Level: {grade_level}, Course Overview: {course_overview}"
            )

        pipeline = RAGpipeline(
            splitter=RecursiveCharacterTextSplitter(chunk_size=100, chunk_overlap=10),
            verbose=verbose,
        )

        pipeline.compile()

        syllabus_builder = SyllabusBuilder(
            subject, grade_level, course_overview, verbose=verbose
        )
        output = syllabus_builder.create_syllabus()
        print(output)

    except LoaderError as e:
        error_message = f"Error in RAGPipeline -> {e}"
        logger.error(error_message)
        raise ToolExecutorError(error_message)

    except ValueError as e:
        logger.error(f"Error creating syllabus: {e}")
        raise ValueError(f"Error creating syllabus: {e}")

    except Exception as e:
        print(traceback.format_exc())
        error_message = f"Error in executor: {e}"
        logger.error(error_message)
        raise ValueError(error_message)

    return output


if __name__ == "__main__":
    executor(
        subject="Data Structures",
        grade_level="University",
        course_overview="This course covers the fundamental concepts and applications of data structures in computer science. Students will explore various data structures such as arrays, linked lists, stacks, queues, trees, and graphs.",
        course_objectives="Students will be equipped with the knowledge to use data structures effectively in real-world applications and advanced computing challenges.",
    )
