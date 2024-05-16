from fastapi import UploadFile
from typing import List

def executor(files: list[str], topic: str, num_questions: int):
    from features.quizzify.tools import RAGpipeline
    from features.quizzify.tools import QuizBuilder
    from features.quizzify.tools import LocalFileLoader  # Updated loader
    
    print(f"Files: {files}")

    # Instantiate RAG pipeline with the local file loader
    pipeline = RAGpipeline(loader=LocalFileLoader)
    
    # Compile the pipeline
    pipeline.compile()

    # Process the uploaded files
    db = pipeline(files)
    
    print(f"{__name__} Executing quiz builder")
    
    print(f"Type of db: {type(db)}")
    print(f"Other variable types: {type(topic)}, {type(num_questions)}")
    
    # Create and return the quiz questions
    return QuizBuilder(db, topic).create_questions(num_questions)

