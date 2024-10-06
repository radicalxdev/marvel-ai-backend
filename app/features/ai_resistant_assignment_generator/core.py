
# Standard library imports
import os
from typing import Any, Dict

# Application-specific imports
from app.services.logger import setup_logger
from app.features.ai_resistant_assignment_generator import AI_resistant #syllabus_generator.tools import Syllabus_generator,Meme_generator_with_reddit,WordGenerator,PDFGenerator
from app.services.schemas import InputData

# Initialize the logger
logger = setup_logger(__name__)

async def executor(inputs: InputData,Type='') -> Dict[str, Any]:
    """
    Executes the tool's functionality and returns a dictionary.

    Args:
        inputs (InputData): The list of inputs for the tool.
        Type (str): The type of output to generate. Defaults to an empty string.

    Returns:
        dict: A dictionary containing tool-specific details.
    """
    try:
        # Initialize input values
        grade = inputs.grade
        assignment = inputs.assignment

        if not grade or not assignment :
            raise ValueError("Missing required parameters: 'grade', 'assignment'")

        gen = AI_resistant(grade, assignment)
        result = gen.run()

        return result

    except Exception as e:
        error_message = f"Error in executor: {e}"
        logger.error(error_message)
        raise ValueError(error_message)
