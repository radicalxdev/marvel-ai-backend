from services.logger import setup_logger

logger = setup_logger()


# TEMPLATE, NEEDS TO BE DISCUSSED AND FORMED ON MONDAY
def executor(
    files,
    topic: str,
    num_questions: int,
    verbose=False,
    *args,
    **kwargs,
):
    try:
        if verbose:
            logger.debug(f"Files: {files}")

        # # Instantiate RAG pipeline with default values
        # pipeline = RAGpipeline(verbose=verbose)
        #
        # pipeline.compile()
        #
        # # Process the uploaded files
        # db = pipeline(files)
        #
        # # Create and return the quiz questions
        # output = QuizBuilder(db, topic, verbose=verbose).create_questions(num_questions)

    # except LoaderError as e:
    #     error_message = e
    #     logger.error(f"Error in RAGPipeline -> {error_message}")
    #     raise ToolExecutorError(error_message)

    except Exception as e:
        error_message = f"Error in executor: {e}"
        logger.error(error_message)
        raise ValueError(error_message)

    return 0
