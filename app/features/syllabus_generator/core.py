# Standard library imports
import os
from typing import Any, Dict

# Application-specific imports
from app.services.logger import setup_logger
from app.features.syllabus_generator.tools import (
    Syllabus_generator,
    Meme_generator_with_reddit,
    WordGenerator,
    PDFGenerator,
)
from app.services.schemas import InputData

# Environment setup
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "local-auth.json"

# Logger initialization
logger = setup_logger(__name__)

async def executor(inputs: InputData, file: Any, Type: str = '') -> Dict[str, Any]:
    """
    Executes the tool's functionality and returns a dictionary.

    Args:
        inputs (InputData): The input data required for generating the syllabus.
        file (Any): The uploaded file object to be processed.
        Type (str): The type of output to generate ('', 'pdf', 'word'). Defaults to an empty string.

    Returns:
        Dict[str, Any]: A dictionary containing the generated output, including files if applicable.

    Raises:
        ValueError: If the provided Type is unsupported or required parameters are missing.
    """

    # Validate the Type parameter
    if Type not in ['', 'pdf', 'word']:
        raise ValueError(f"Unsupported Type: {Type}")

    try:
        # Extract input values
        grade = inputs.grade
        subject = inputs.subject
        syllabus_type = inputs.Syllabus_type
        instructions = inputs.instructions
        content = await file.read()  # Read file content asynchronously

        # Validate compulsory parameters
        if not grade or not subject:
            raise ValueError("Missing required parameters: 'grade', 'subject'")

        # Generate memes related to the subject
        Memes_Generator = Meme_generator_with_reddit(subject=subject)
        memes = Memes_Generator.get_memes()

        # Generate the syllabus
        Syllabus_Generator = Syllabus_generator(
            grade=grade,
            subject=subject,
            syllabus_type=syllabus_type,
            instructions=instructions,
            content=content,
            path="app/features/syllabus_generator/"
        )
        result = Syllabus_Generator.run()
        result['memes'] = memes  # Include memes in the result

        # Handle specific output types: PDF or Word document
        if Type == 'pdf':
            pdf_gen = PDFGenerator(grade, subject)
            return {
                'file': pdf_gen.generate_pdf(result),
                'type': 'application/pdf'
            }
        elif Type == 'word':
            word_gen = WordGenerator(grade, subject)
            return {
                'file': word_gen.generate_word(result),
                'type': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            }

        # Return the result dictionary if no specific Type is given
        return result

    except Exception as e:
        # Log and re-raise the exception with a detailed message
        error_message = f"Error in executor: {e}"
        logger.error(error_message)
        raise ValueError(error_message)
