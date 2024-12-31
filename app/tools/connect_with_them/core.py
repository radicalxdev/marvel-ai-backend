from app.utils.document_loaders import get_docs
from app.tools.connect_with_them.tools import AIConnectWithThemGenerator
from app.services.schemas import ConnectWithThemArgs
from app.services.logger import setup_logger
from app.api.error_utilities import LoaderError, ToolExecutorError

logger = setup_logger()

def executor(grade_level: str,
             task_description: str,
             students_description: str,
             task_description_file_url: str,
             task_description_file_type: str,
             student_description_file_url: str,
             student_description_file_type: str,
             lang: str,
             verbose=False):
    
    try:
        if(task_description_file_type):
            logger.info(f"Generating docs. from {task_description_file_type}")
        if(student_description_file_type):
            logger.info(f"Generating docs. from {student_description_file_type}")

        docs = None

        def fetch_docs(file_url, file_type):
            return get_docs(file_url, file_type, True) if file_url and file_type else None

        task_description_docs = fetch_docs(task_description_file_url, task_description_file_type)
        student_description_docs = fetch_docs(student_description_file_url, student_description_file_type)

        docs = (
            task_description_docs + student_description_docs
            if task_description_docs and student_description_docs
            else task_description_docs or student_description_docs
        )

        connect_with_them_args = ConnectWithThemArgs(
            grade_level=grade_level,
            task_description=task_description,
            students_description=students_description,
            task_description_file_url=task_description_file_url,
            task_description_file_type=task_description_file_type,
            student_description_file_url=student_description_file_url,
            student_description_file_type=student_description_file_type,
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
