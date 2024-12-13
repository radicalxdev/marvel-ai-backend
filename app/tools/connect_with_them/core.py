from app.utils.document_loaders import get_docs
from app.tools.connect_with_them.tools import AIConnectWithThemGenerator
from app.services.schemas import ConnectWithThemArgs
from app.services.logger import setup_logger
from app.api.error_utilities import LoaderError, ToolExecutorError

logger = setup_logger()

def executor(grade_level: str,
             task_description: str,
             students_description: str,
             td_file_url: str,
             td_file_type: str,
             sd_file_url: str,
             sd_file_type: str,
             lang: str,
             verbose=False):
    
    try:
        if(td_file_type):
            logger.info(f"Generating docs. from {td_file_type}")
        if(sd_file_type):
            logger.info(f"Generating docs. from {sd_file_type}")

        docs = None

        def fetch_docs(file_url, file_type):
            return get_docs(file_url, file_type, True) if file_url and file_type else None

        task_description_docs = fetch_docs(td_file_url, td_file_type)
        student_description_docs = fetch_docs(sd_file_url, sd_file_type)

        docs = (
            task_description_docs + student_description_docs
            if task_description_docs and student_description_docs
            else task_description_docs or student_description_docs
        )

        connect_with_them_args = ConnectWithThemArgs(
            grade_level=grade_level,
            task_description=task_description,
            students_description=students_description,
            td_file_url=td_file_url,
            td_file_type=td_file_type,
            sd_file_url=sd_file_url,
            sd_file_type=sd_file_type,
            lang=lang
        )

        output = AIConnectWithThemGenerator(args=connect_with_them_args, verbose=verbose).generate_suggestion(docs)

        logger.info(f"Connect with Them assignments generated successfully")

    except LoaderError as e:
        error_message = e
        logger.error(f"Error in the Connect with Them Assignment Generator Pipeline -> {error_message}")
        raise ToolExecutorError(error_message)
    
    except Exception as e:
        error_message = f"Error in executor: {e}"
        logger.error(error_message)
        raise ValueError(error_message)
    
    return output
