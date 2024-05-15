from fastapi import UploadFile
from typing import List


def executor(files: list, topic: str, num_questions: int):
    from features.quizzify.tools import RAGpipeline
    from features.quizzify.tools import QuizBuilder
    from features.quizzify.tools import GCSLoader
    
    ## Instantiate RAG pipeline
    pipeline = RAGpipeline(loader = GCSLoader)
    
    ## Create pipeline
    pipeline.compile()

    db = pipeline(files)
    
    return QuizBuilder(db, topic).create_questions(num_questions)
    

