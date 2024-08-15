# Standard library imports
import os
from typing import Any, Dict

# Application-specific imports
from app.services.logger import setup_logger
from app.features.syllabus_generator.tools import Syllabus_generator,Meme_generator_with_reddit,WordGenerator,PDFGenerator
from app.services.schemas import InputData

# Initialize the logger
logger = setup_logger(__name__)

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "local-auth.json"


async def executor(inputs: InputData,Type='') -> Dict[str, Any]:
    """
    Executes the tool's functionality and returns a dictionary.

    Args:
        inputs (InputData): The list of inputs for the tool.
        Type (str): The type of output to generate. Defaults to an empty string.

    Returns:
        dict: A dictionary containing tool-specific details.
    """
    if Type not in ['','pdf','word'] :
        raise ValueError(f"Unsupported Type: {Type}")

    try:
        grade = inputs.grade
        subject = inputs.subject
        syllabus_type = inputs.Syllabus_type
        instructions = inputs.instructions
        if not grade or not subject or not syllabus_type:
            raise ValueError("Missing required parameters: 'grade', 'subject', or 'Syllabus_type'")

        Memes_Generator = Meme_generator_with_reddit(subject=subject)
        memes = Memes_Generator.get_memes()
        Syllabus_Generator = Syllabus_generator(grade,subject,syllabus_type,instructions,path="app/features/syllabus_generator/")
        result = Syllabus_Generator.run()
        result['memes'] = memes

        if Type == 'pdf':
            Gen = PDFGenerator(grade,subject)
            return {
                    'file' :Gen.generate_pdf(result),
                    'type' : 'application/pdf'
                    }
        elif Type == 'word':
            Gen = WordGenerator(grade,subject)
            return {
                    'file' :Gen.generate_word(result),
                    'type' : 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
                    }
            
        return result

    except Exception as e:
        error_message = f"Error in executor: {e}"
        logger.error(error_message)
        raise ValueError(error_message)
