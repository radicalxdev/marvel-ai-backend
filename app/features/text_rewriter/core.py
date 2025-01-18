from app.services.logger import setup_logger
from app.api.error_utilities import LoaderError, ToolExecutorError
from app.utils.document_loaders import get_docs
from app.features.text_rewriter.tools import TextRewriterPipeline
from app.services.schemas import TextRewriterArgs
logger = setup_logger()

def executor(
        text: str,
        instructions: str,
        file_url: str,
        file_type: str,
        lang: str,
        verbose=True
        ):
    
    try:
        if verbose:
            if file_url:
                logger.info(f"File URL loaded: {file_url}")
            if file_type:
                logger.info(f"File Type loaded: {file_type}")
        docs = None 
        if file_url and file_type:
            docs = get_docs(file_url, file_type, lang=lang, verbose=True)

        text_rewriter_args = TextRewriterArgs(
            text=text,
            instructions=instructions,
            file_type=file_type,
            file_url=file_url,
            lang=lang
        )

        output = TextRewriterPipeline(args=text_rewriter_args, verbose=True).re_writer(docs)
        if output:
            logger.info(f"Text Rewritten successfully")
        
            
    except LoaderError as e:
        error_message = e
        logger.error(f"Error in Text Rewriter Pipeline -> {error_message}")
        raise ToolExecutorError(error_message)
    
    except Exception as e:
        error_message = f"Error in executor: {e}"
        logger.error(error_message)
        raise ValueError(error_message)

    return output