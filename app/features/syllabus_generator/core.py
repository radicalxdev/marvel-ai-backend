from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders.text import TextLoader
from app.services.tool_registry import ToolFile
from services.logger import setup_logger
from app.features.syllabus_generator.tools import SyllabusBuilder
from app.api.error_utilities import LoaderError, ToolExecutorError
from dotenv import load_dotenv

logger = setup_logger()


def executor(
    subject: str,
    grade_level: str,
    course_overview: str,
    customisation: str,
    options: List[str],
    verbose: bool = True,
    **kwargs,
):
    """Execute the syllabus generation process."""
    try:
        if verbose:
            logger.debug(
                f"Subject: {subject}, Grade Level: {grade_level}, Course Overview: {course_overview}"
            )

        sb = SyllabusBuilder(
            subject,
            grade_level,
            course_overview,
            customisation,
            options,
            verbose=verbose,
        )
        syllabus = sb.create_syllabus()

        # updated_syllabus = sb.apply_customisation(syllabus)
        # print(updated_syllabus)

    except LoaderError as e:
        error_message = f"Error in RAGPipeline -> {e}"
        logger.error(error_message)
        raise ToolExecutorError(error_message)

    except ValueError as e:
        logger.error(f"Error creating syllabus: {e}")
        raise ValueError(f"Error creating syllabus: {e}")

    except Exception as e:
        error_message = f"Error in executor: {e}"
        logger.error(error_message)
        raise ValueError(error_message)

    return syllabus


if __name__ == "__main__":
    load_dotenv()
    s = SyllabusBuilder(
        subject="Data Structures",
        grade_level="University",
        course_overview="This course covers the fundamental concepts and applications of data structures in computer science. Students will explore various data structures such as arrays, linked lists, stacks, queues, trees, and graphs.",
        options=["title", "overview"],
        customisation="",
    )
    t = s.create_syllabus()
    print(t)
