# Standard library imports
import os
from typing import Any, Dict

# Third-party imports
from dotenv import load_dotenv, find_dotenv
from pydantic import BaseModel, Field
from typing import List, Optional

# Application-specific imports
from app.services.logger import setup_logger
from app.features.syllabus_generator.tools import Syllabus_generator, Doc_Generator

# Initialize the logger
logger = setup_logger(__name__)

# Load environment variables from a .env file
load_dotenv(find_dotenv())

# Retrieve API key and Search Engine ID from environment variables
API_KEY = os.getenv('API_KEY')
SEARCH_ENGINE_ID = os.getenv('SEARCH_ENGINE_ID')

# Set the path for Google application credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "local-auth.json"

# Define a Pydantic model for input data
class InputData(BaseModel):
    grade: str  # Grade level
    subject: str  # Subject name
    Syllabus_type: Optional[str] = 'exam_based'  # Type of syllabus, default is 'exam_based'
    instructions: Optional[str] = 'None'  # Additional instructions, default is 'None'

# Function to execute tool functionality based on tool ID and inputs
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
        # Extract input parameters
        grade = inputs.grade
        subject = inputs.subject
        syllabus_type = inputs.Syllabus_type
        instructions = inputs.instructions
        
        # Check for missing required parameters
        if not grade or not subject or not syllabus_type:
            raise ValueError("Missing required parameters: 'grade', 'subject', or 'Syllabus_type'")
        
        # Create a Syllabus_generator object
        Generator = Syllabus_generator(
            grade=grade,
            subject=subject,
            Syllabus_type=syllabus_type,
            instructions=instructions,
            API_KEY=API_KEY,
            SEARCH_ENGINE_ID=SEARCH_ENGINE_ID,
            path="app/features/syllabus_generator/"
        )

        # Run the syllabus generation process
        result = Generator.run(verbose=True)

        # Return result based on the tool ID
        if tool_id == 1:
            return result

        # Create a Doc_Generator object
        generator = Doc_Generator(grade, subject)

        if tool_id == 2:
            return generator.generate_pdf(result)

        if tool_id == 3:
            return generator.generate_word(result)

        raise ValueError(f"Unsupported tool_id: {tool_id}")

    except Exception as e:
        error_message = f"Error in executor: {e}"
        logger.error(error_message)
        raise ValueError(error_message)
