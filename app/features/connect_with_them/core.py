from app.features.connect_with_them.document_loaders import get_docs
from app.features.connect_with_them.tools import AIConnectWithThemGenerator
from app.services.schemas import ConnectWithThemArgs
from app.services.logger import setup_logger
from app.api.error_utilities import LoaderError, ToolExecutorError

logger = setup_logger()

def executor(connect_with_them_args: ConnectWithThemArgs, verbose=False):
    
    try:
        if verbose: print(f"Args.: {connect_with_them_args}")

        logger.info(f"Generating docs. from {connect_with_them_args.file_type}")

        docs = get_docs(connect_with_them_args.file_url, connect_with_them_args.file_type, True)

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
