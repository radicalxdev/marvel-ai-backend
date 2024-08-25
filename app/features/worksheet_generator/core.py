# import sys
# import os
from features.quizzify.tools import RAGpipeline
from services.tool_registry import ToolFile
from services.logger import setup_logger
from features.worksheet_generator.tools import WorksheetBuilder
from api.error_utilities import LoaderError, ToolExecutorError
logger = setup_logger()


def executor(files: list[ToolFile], topic: str, level: str, hint: str, hint_num: int, num_questions: int, verbose=True):
    try:
        if verbose: logger.debug(f"Files: {files}")
        # Instantiate RAG pipeline with default values
        pipeline = RAGpipeline(verbose=verbose)
        pipeline.compile()
        # Process the uploaded files
        db = pipeline(files)

        # Create and return the quiz questions
        output = WorksheetBuilder(db, topic, level, hint, "quiz").create_questions(num_questions)
        output.extend(WorksheetBuilder(db, topic, level, hint, "worksheet").create_worksheet_questions(hint_num))

    # Try-Except blocks on custom defined exceptions to provide better logging
    except LoaderError as e:
        error_message = e
        logger.error(f"Error in RAGPipeline -> {error_message}")
        raise ToolExecutorError(error_message)

    # These help differentiate user-input errors and internal errors. Use 4XX and 5XX status respectively.
    except Exception as e:
        error_message = f"Error in executor: {e}"
        logger.error(error_message)
        raise ValueError(error_message)

    return output

# executor([ToolFile(url="https://courses.edx.org/asset-v1:ColumbiaX+CSMM.101x+1T2017+type@asset+block@AI_edx_ml_5.1intro.pdf")],
#          "machine learning","Masters","single sentence answer questions",5, 5)