# tools.py

def process_files(files: list, verbose: bool = False):
    """
    Process uploaded files and convert them into a format usable by the pipeline.
    
    Args:
        files (list): List of uploaded files.
        verbose (bool): Enable detailed logging if True.
    
    Returns:
        Database object containing processed data.
    """
    pipeline = RAGpipeline(verbose=verbose)
    pipeline.compile()
    return pipeline(files)

def generate_questions(db, topic: str, num_questions: int, verbose: bool = False):
    """
    Generate quiz questions based on the processed data.
    
    Args:
        db: Processed data.
        topic (str): Topic of the quiz.
        num_questions (int): Number of questions to generate.
        verbose (bool): Enable detailed logging if True.
    
    Returns:
        list: Generated quiz questions.
    """
    return QuizBuilder(db, topic, verbose=verbose).create_questions(num_questions)
