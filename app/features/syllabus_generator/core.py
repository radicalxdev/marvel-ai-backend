# Standard library imports
import os
from typing import Any, Dict

# Third-party imports
from dotenv import load_dotenv,find_dotenv
from pydantic import BaseModel, Field
from typing import List, Optional

# Application-specific imports
from app.services.logger import setup_logger
from app.features.syllabus_generator.tools import Syllabus_generator,Doc_Generator


logger = setup_logger(__name__)

load_dotenv(find_dotenv())

API_KEY = os.getenv('API_KEY')
SEARCH_ENGINE_ID = os.getenv('SEARCH_ENGINE_ID')


os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "local-auth.json"

class InputData(BaseModel):
    grade: str
    subject: str
    Syllabus_type: Optional[str] = 'exam_based'
    instructions : Optional[str] = 'None'

def executor(tool_id: int, inputs: InputData) -> Dict[str, Any]:
    """
    Executes the tool's functionality and returns a dictionary.

    Args:
        tool_id (int): The ID of the tool to use.
        inputs (InputData): The list of inputs for the tool.

    Returns:
        dict: A dictionary containing tool-specific details.
    """
    try:
         # Assume tool_id 1 corresponds to generating a syllabus
        grade = inputs.grade
        subject = inputs.subject
        syllabus_type = inputs.Syllabus_type
        instructions = inputs.instructions
        if not grade or not subject or not syllabus_type:
            raise ValueError("Missing required parameters: 'grade', 'subject', or 'Syllabus_type'")
        # Execute the syllabus generation logic
        Generator = Syllabus_generator(grade=grade,
                                       subject=subject,
                                       Syllabus_type=syllabus_type,
                                       instructions = instructions,
                                       API_KEY=API_KEY,
                                       SEARCH_ENGINE_ID=SEARCH_ENGINE_ID,
                                       path="app/features/syllabus_generator/")

        result = Generator.run(verbose=True)

        if tool_id == 1:
            return result

        generator = Doc_Generator(grade,subject)

        if tool_id == 2:
            return generator.generate_pdf(result)

        if tool_id == 3:
            return generator.generate_word(result)

        raise ValueError(f"Unsupported tool_id: {tool_id}")

    except Exception as e:
        error_message = f"Error in executor: {e}"
        logger.error(error_message)
        raise ValueError(error_message)
