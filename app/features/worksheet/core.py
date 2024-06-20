from services.tool_registry import ToolFile
from services.logger import setup_logger
from features.worksheet.tools import WorksheetBuilder
from api.error_utilities import LoaderError, ToolExecutorError

logger = setup_logger()

def executor(topic: str, grade_level: str, num_worksheets: int, num_multiple_choice: int, verbose=False):
    try:
        
        # Create and return the worksheets
        output = WorksheetBuilder(topic = topic, grade_level = grade_level, verbose=verbose).create_worksheets(num_worksheets, num_multiple_choice)
        
        ## DEBUG print (remove later)
        for i, w in enumerate(output):
            print("Worksheet:", i + 1)
            print(w)

    except LoaderError as e:
        error_message = e
        logger.error(f"Error in WorksheetBuilder -> {error_message}")
        raise ToolExecutorError(error_message)
    
    except Exception as e:
        error_message = f"Error in executor: {e}"
        logger.error(error_message)
        raise ValueError(error_message)
    
    return output