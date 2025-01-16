from app.services.logger import setup_logger
from app.utils.document_loaders import get_docs
from app.features.text_rewriter.tools import TextRewriter
from app.api.error_utilities import ToolExecutorError

logger = setup_logger()

def executor(
             instructions: str,
             file_url: str,
             file_type: str, 
             verbose=False):
    
    try:
        if verbose:
            logger.info(f"File URL loaded: {file_url}")
        
        if file_type and file_url:
            logger.info(f"Generating docs. from {file_url} with type {file_type}")
            docs = get_docs(file_url, file_type, verbose=True)
        else:
            docs = None
            raise ToolExecutorError("File URL and file type must be provided")
        
        output = TextRewriter(instructions, verbose=verbose).rewrite(docs)

    except Exception as e:
        error_message = f"Error in executor: {e}"
        logger.error(error_message)
        raise ValueError(error_message)
    
    return output

