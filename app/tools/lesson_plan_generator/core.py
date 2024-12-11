from app.tools.lesson_plan_generator.tools import LessonPlanGeneratorPipeline
from app.services.schemas import LessonPlanGeneratorArgs
from app.utils.document_loaders import get_docs
from app.services.logger import setup_logger
from app.api_config.error_utilities import LoaderError, ToolExecutorError

logger = setup_logger()

def executor(grade_level: str,
             topic: str,
             objectives: str,
             additional_customization: str,
             objectives_file_url: str,
             objectives_file_type: str,
             ac_file_url: str,
             ac_file_type: str,
             lang: str, 
             verbose=False):
    
    try:
        if objectives_file_type:
            logger.info(f"Generating docs. from {objectives_file_type}")
        if ac_file_type:
            logger.info(f"Generating docs. from {ac_file_type}")

        docs = None

        def fetch_docs(file_url, file_type):
            return get_docs(file_url, file_type, True) if file_url and file_type else None

        objectives_docs = fetch_docs(objectives_file_url, objectives_file_type)
        additional_customization_docs = fetch_docs(ac_file_url, ac_file_type)

        docs = (
            objectives_docs + additional_customization_docs
            if objectives_docs and additional_customization_docs
            else objectives_docs or additional_customization_docs
        )

        lesson_plan_generator_args = LessonPlanGeneratorArgs(
            grade_level=grade_level,
            topic=topic,
            objectives=objectives,
            additional_customization=additional_customization,
            objectives_file_url=objectives_file_url,
            objectives_file_type=objectives_file_type,
            ac_file_url=ac_file_url,
            ac_file_type=ac_file_type,
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
