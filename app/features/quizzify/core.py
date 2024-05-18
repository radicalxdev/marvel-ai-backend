from services.tool_registry import ToolFile
from services.logger import setup_logger
from features.quizzify.tools import RAGpipeline
from features.quizzify.tools import QuizBuilder

logger = setup_logger()

def executor(files: list[ToolFile], topic: str, num_questions: int, verbose=False):
    
    if verbose:
        logger.info(f"Files: {files}")

    # Instantiate RAG pipeline with default values
    pipeline = RAGpipeline(verbose=verbose)
    
    pipeline.compile()
    
    # Process the uploaded files
    db = pipeline(files)
    
    # Create and return the quiz questions
    output = QuizBuilder(db, topic, verbose=verbose).create_questions(num_questions)
    
    
    return output

