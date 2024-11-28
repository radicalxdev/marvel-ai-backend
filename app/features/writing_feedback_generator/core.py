from app.features.writing_feedback_generator.tools import WritingFeedbackGeneratorPipeline
from app.services.schemas import WritingFeedbackGeneratorArgs
from app.utils.document_loaders import get_docs
from app.services.logger import setup_logger
from app.api.error_utilities import LoaderError, ToolExecutorError

logger = setup_logger()

def executor(grade_level: str,
             assignment_description: str,
             criteria: str,
             writing_to_review: str,
             file_url: str,
             file_type: str,
             lang: str, 
             verbose=False):
    
    try:
        if (file_url and file_type):
            logger.info(f"Generating docs. from {file_type}")
            docs = get_docs(file_url, file_type, True)
        else:
            docs = None

        writing_feedback_generator = WritingFeedbackGeneratorArgs(
            grade_level=grade_level,
            assignment_description=assignment_description,
            criteria=criteria,
            writing_to_review=writing_to_review,
            file_type=file_type,
            file_url=file_url,
            lang=lang
        )

        output = WritingFeedbackGeneratorPipeline(args=writing_feedback_generator, verbose=verbose).generate_feedback(docs)

        logger.info(f"Writing Feedback generated successfully")

    except LoaderError as e:
        error_message = e
        logger.error(f"Error in Writing Feedback Generator Pipeline -> {error_message}")
        raise ToolExecutorError(error_message)
    
    except Exception as e:
        error_message = f"Error in executor: {e}"
        logger.error(error_message)
        raise ValueError(error_message)
    
    return output