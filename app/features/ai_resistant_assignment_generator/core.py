# Standard library imports
import os
from typing import Any, Dict

#python3 -m uvicorn app.main:app --reload
from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
from app.services.logger import setup_logger
from app.features.connect_with_them.tools import Agent_executor
from app.features.connect_with_them.prompt.Prompts import Prompt_query
from typing import Optional

# Application-specific imports
from app.services.logger import setup_logger
from app.features.ai_resistant_assignment_generator.tools import AIRAG 
#syllabus_generator.tools import Syllabus_generator,Meme_generator_with_reddit,WordGenerator,PDFGenerator
from app.services.schemas import InputData, AIRAGRequest
# Initialize the logger
logger = setup_logger(__name__)

class ExecutorRequest(BaseModel):
    grade: str
    assignment: str
    description: Optional[str] = None

app = FastAPI()

@app.post("/execute/")
async def executor(inputs: AIRAGRequest, Type: str = '',file: UploadFile = File(None)) -> Dict[str, Any]:
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
        description = inputs.assignment

        if not grade or not assignment :
            raise ValueError("Missing required parameters: 'grade', 'assignment'")

        gen = AIRAG(grade, assignment, description)
        result = gen.run()

        return result

    except Exception as e:
        error_message = f"Error in executor: {e}"
        logger.error(error_message)
        raise ValueError(error_message)
