from fastapi import UploadFile
from typing import List


def executor(upload_files: List[UploadFile], topic: str, num_questions: int):
    from features.quizzify.tools import RAGpipeline
    from features.quizzify.tools import QuizBuilder
    
    ## Instantiate RAG pipeline
    pipeline = RAGpipeline() # default pipeline
    
    ## Create pipeline
    pipeline.compile()

    db = pipeline(upload_files)
    
    response = QuizBuilder(db, topic).create_questions(num_questions)
    
    return {"data": response}
    

