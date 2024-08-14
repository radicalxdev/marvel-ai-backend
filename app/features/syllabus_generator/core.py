from typing import List
from services.logger import setup_logger
from app.features.syllabus_generator.tools import SyllabusBuilder
from app.api.error_utilities import LoaderError, ToolExecutorError

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
