from app.features.quizzify.tools import RAGpipeline
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders.text import TextLoader
from services.logger import setup_logger
from app.features.syllabus_generator.tools import SyllabusBuilder

logger = setup_logger()


# TEMPLATE, NEEDS TO BE DISCUSSED AND FORMED ON MONDAY
def executor(
    subject: str,
    grade_level: str,
    files,
    verbose=False,
):
    try:
        if verbose:
            logger.debug(f"Subject: {subject}, grade_level: {grade_level}")

        # Instantiate RAG pipeline with default values
        pipeline = RAGpipeline(
            splitter=RecursiveCharacterTextSplitter(
                chunk_size=100, chunk_overlap=10
            ),  # smaller chunks cause probably less data input for what will be used for atm
            verbose=verbose,
        )

        pipeline.compile()

        # Process the extra guidance
        db = pipeline(files)

        # Create and return the quiz questions
        output = SyllabusBuilder(
            db, subject, grade_level, verbose=verbose
        ).create_syllabus()
        print(output)

    # except LoaderError as e:
    #     error_message = e
    #     logger.error(f"Error in RAGPipeline -> {error_message}")
    #     raise ToolExecutorError(error_message)

    except Exception as e:
        error_message = f"Error in executor: {e}"
        logger.error(error_message)
        raise ValueError(error_message)

    return 0


if __name__ == "__main__":
    executor(subject="Multiplication", grade_level="K12", files=None)
