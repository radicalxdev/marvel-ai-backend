# This is code from quizbuilder - repurpose for syllabus generator
from services.logger import setup_logger

logger = setup_logger()

def executor(grade_level: str | int, topic: str, context: str, verbose=False):
    
    try:
        if verbose: logger.debug(f"Files: {files}")

        # Instantiate RAG pipeline with default values
        pipeline = RAGpipeline(verbose=verbose)
        
        pipeline.compile()
        

    except LoaderError as e:
        error_message = e
        logger.error(f"Error in RAGPipeline -> {error_message}")
        raise ToolExecutorError(error_message)
    
    except Exception as e:
        error_message = f"Error in executor: {e}"
        logger.error(error_message)
        raise ValueError(error_message)
    
    return output

