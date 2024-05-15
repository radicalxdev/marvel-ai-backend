# from fastapi import UploadFile
# from typing import List


# def executor(files: list, topic: str, num_questions: int):
#     from features.quizzify.tools import RAGpipeline
#     from features.quizzify.tools import QuizBuilder
#     from features.quizzify.tools import GCSLoader
    
#     ## Instantiate RAG pipeline
#     pipeline = RAGpipeline(loader = GCSLoader)
    
#     ## Create pipeline
#     pipeline.compile()

#     db = pipeline(files)
    
#     return QuizBuilder(db, topic).create_questions(num_questions)
from fastapi import UploadFile
from typing import List

def executor(files: List[UploadFile], topic: str, num_questions: int):
    from features.quizzify.tools import RAGpipeline
    from features.quizzify.tools import QuizBuilder
    from features.quizzify.tools import UploadPDFLoader  # Updated loader

    # Instantiate RAG pipeline with the local file loader
    pipeline = RAGpipeline(loader=UploadPDFLoader)
    
    # Compile the pipeline
    pipeline.compile()

    # Process the uploaded files
    db = pipeline.load_PDFs(files)
    
    # Create and return the quiz questions
    return QuizBuilder(db, topic).create_questions(num_questions)
