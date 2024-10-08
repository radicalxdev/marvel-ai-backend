# Standard library imports
import os
from typing import Any, Dict

from fastapi import FastAPI, HTTPException, UploadFile, File
#from pydantic import BaseModel
from app.services.logger import setup_logger
from app.features.connect_with_them.tools import Agent_executor
from app.features.connect_with_them.prompt.Prompts import Prompt_query
from typing import Optional
import docx
import PyPDF2
import io

# Application-specific imports
from app.services.logger import setup_logger
from app.features.ai_resistant_assignment_generator import AI_resistant #syllabus_generator.tools import Syllabus_generator,Meme_generator_with_reddit,WordGenerator,PDFGenerator
from app.services.schemas import InputData

# Initialize the logger
logger = setup_logger(__name__)

# class ExecutorRequest(BaseModel):
#     grade: Optional[str]
#     subject: Optional[str]
#     description: Optional[str] = None

def read_pdf(file: UploadFile):
    try:
        pdf_reader = PyPDF2.PdfReader(file.file)
        text = ''
        for page_num in range(len(pdf_reader.pages)):
            text += pdf_reader.pages[page_num].extract_text()
        return text
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading PDF file: {e}")

def read_docx(file: UploadFile):
    try:
        doc = docx.Document(file.file)
        full_text = []
        for para in doc.paragraphs:
            full_text.append(para.text)
        return '\n'.join(full_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading DOCX file: {e}")

def read_txt(file: UploadFile):
    try:
        content = file.file.read().decode('utf-8')
        return content
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading TXT file: {e}")

app = FastAPI()

@app.post("/execute/")
async def executor(inputs: InputData,Type='',file: Optional[UploadFile] = File(None)) -> Dict[str, Any]:
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

        # If file is uploaded, process it
        if file:
            if file.filename.endswith(".pdf"):
                description = read_pdf(file)
            elif file.filename.endswith(".docx"):
                description = read_docx(file)
            elif file.filename.endswith(".txt"):
                description = read_txt(file)
            else:
                raise HTTPException(status_code=400, detail="Unsupported file type. Please upload a PDF, DOCX, or TXT file.")

            if not grade or not assignment :
                raise ValueError("Missing required parameters: 'grade', 'assignment'")

        gen = AI_resistant(grade, description)
        result = gen.run()

        return result

    except Exception as e:
        error_message = f"Error in executor: {e}"
        logger.error(error_message)
        raise ValueError(error_message)
