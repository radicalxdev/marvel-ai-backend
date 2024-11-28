from app.features.lesson_plan_generator.tools import LessonPlanGeneratorPipeline
from app.services.schemas import LessonPlanGeneratorArgs
from app.utils.document_loaders import get_docs
from app.services.logger import setup_logger
from app.api.error_utilities import LoaderError, ToolExecutorError

logger = setup_logger()

def executor(grade_level: str,
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

        lesson_plan_generator_args = LessonPlanGeneratorArgs(
            grade_level=grade_level,
            topic=topic,
            objectives=objectives,
            additional_comments=additional_comments,
            file_type=file_type,
            file_url=file_url,
            lang=lang
        )

        output = LessonPlanGeneratorPipeline(args=lesson_plan_generator_args, verbose=verbose).generate_lesson_plan(docs)

        logger.info(f"Lesson Plan generated successfully")

    except LoaderError as e:
        error_message = e
        logger.error(f"Error in Lesson Plan Generator Pipeline -> {error_message}")
        raise ToolExecutorError(error_message)
    
    except Exception as e:
        error_message = f"Error in executor: {e}"
        logger.error(error_message)
        raise ValueError(error_message)
    
    return output
