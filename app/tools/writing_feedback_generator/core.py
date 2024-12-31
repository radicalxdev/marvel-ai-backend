from app.tools.writing_feedback_generator.tools import WritingFeedbackGeneratorPipeline
from app.services.schemas import WritingFeedbackGeneratorArgs
from app.utils.document_loaders import get_docs
from app.services.logger import setup_logger
from app.api.error_utilities import LoaderError, ToolExecutorError

logger = setup_logger()

def executor(grade_level: str,
             assignment_description: str,
             criteria: str,
             writing_to_review: str,
             criteria_file_url: str,
             criteria_file_type: str,
             writing_to_review_file_url: str,
             writing_to_review_file_type: str,
             lang: str, 
             verbose=False):
    
    try:
        if (criteria_file_type):
            logger.info(f"Generating docs. from {criteria_file_type}")
        
        if (writing_to_review_file_type):
            logger.info(f"Generating docs. from {writing_to_review_file_type}")

        docs = None

        def fetch_docs(file_url, file_type):
            return get_docs(file_url, file_type, True) if file_url and file_type else None

        criteria_docs = fetch_docs(criteria_file_url, criteria_file_type)
        wtr_docs = fetch_docs(writing_to_review_file_url, writing_to_review_file_type)

        docs = (
            criteria_docs + wtr_docs
            if criteria_docs and wtr_docs
            else criteria_docs or wtr_docs
        )

        writing_feedback_generator = WritingFeedbackGeneratorArgs(
            grade_level=grade_level,
            assignment_description=assignment_description,
            criteria=criteria,
            writing_to_review=writing_to_review,
            criteria_file_url=criteria_file_url,
            criteria_file_type=criteria_file_type,
            writing_to_review_file_url=writing_to_review_file_url,
            writing_to_review_file_type=writing_to_review_file_type,
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