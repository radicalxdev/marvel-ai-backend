from app.features.presentation_generator.document_loaders import get_docs
from app.features.presentation_generator.tools import PresentationGenerator
from app.services.schemas import PresentationGeneratorInput
from app.services.logger import setup_logger
from app.api.error_utilities import LoaderError, ToolExecutorError

logger = setup_logger()

def executor(grade_level: str,
             n_slides: int,
             topic: str,
             objectives: str,
             additional_comments: str,
             file_url: str,
             file_type: str,
             lang: str, 
             verbose=False):

    try:
        logger.info(f"Generating docs. from {file_type}")

        docs = get_docs(file_url, file_type, True)

        presentation_generator_args = PresentationGeneratorInput(
            grade_level=grade_level,
            n_slides=n_slides,
            topic=topic,
            objectives=objectives,
            additional_comments=additional_comments,
            file_url=file_url,
            file_type=file_type,
            lang=lang
        )

        output = PresentationGenerator(args=presentation_generator_args, verbose=verbose).generate_presentation(docs)

        logger.info(f"Presentation generated successfully")

    except LoaderError as e:
        error_message = e
        logger.error(f"Error in Presentation Generator Pipeline -> {error_message}")
        raise ToolExecutorError(error_message)

    except Exception as e:
        error_message = f"Error in executor: {e}"
        logger.error(error_message)
        raise ValueError(error_message)

    return output