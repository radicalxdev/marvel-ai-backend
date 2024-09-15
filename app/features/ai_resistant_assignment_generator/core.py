from services.logger import setup_logger
from tools import process_files, generate_questions

logger = setup_logger()


def executor(files: list, topic: str, num_questions: int, verbose: bool = False):
    try:
        if verbose:
            logger.debug(f"Received files: {files}, Topic: {topic}, Num of Questions: {num_questions}")
        
        db = process_files(files, verbose)
        output = generate_questions(db, topic, num_questions, verbose)
        
        if verbose:
            logger.debug(f"Generated questions: {output}")
        
        return output

    except LoaderError as e:
        error_message = f"Loader error: {e}"
        logger.error(error_message)
        raise ToolExecutorError(error_message)

    except Exception as e:
        error_message = f"Error in executor: {e}"
        logger.error(error_message)
        raise ValueError(error_message)
