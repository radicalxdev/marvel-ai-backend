from app.utils.document_loaders import get_docs
from app.features.connect_with_them.tools import AIConnectWithThemGenerator
from app.services.schemas import ConnectWithThemArgs
from app.services.logger import setup_logger
from app.api.error_utilities import LoaderError, ToolExecutorError

logger = setup_logger()

def executor(grade_level: str,
             task_description: str,
             students_description: str,
             file_url: str,
             file_type: str,
             lang: str,
             verbose=False):
    
    try:
        logger.info(f"Generating docs. from {file_type}")

        docs = get_docs(file_url, file_type, True)

        connect_with_them_args = ConnectWithThemArgs(
            grade_level=grade_level,
            task_description=task_description,
            students_description=students_description,
            file_url=file_url,
            file_type=file_type,
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
