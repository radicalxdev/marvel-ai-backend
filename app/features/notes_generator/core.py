import os
import re
from typing import Literal, Optional, Dict
import logging
from tools import (
    extract_text_from_file, 
    extract_text_from_url, 
    generate_notes, 
    export_notes
)

def executor(input_type: Literal['text', 'file', 'url'],
             input_content: Optional[str] = None,
             file_path: Optional[str] = None,
             focus_topic: Optional[str] = None,
             output_structure: Literal['bullet', 'paragraph', 'table'] = 'bullet',
             export_format: Literal['txt', 'docx', 'pdf'] = 'txt') -> Dict[str, str]:
    print("Current working directory:", os.getcwd())
    
    """
    Main executor function for Notes Generator Tool.
    Parameters:
            input_type (str): Type of input - 'text', 'file', or 'url'.
            input_content (str): Direct text input (if input_type='text').
            file_path (str): Path to uploaded file (if input_type='file').
            focus_topic (str): Topic or focus for notes generation.
            output_structure (str): Format for notes - bullet, paragraph, or table.
            export_format (str): Export format - txt, docx, or pdf.
        Returns:
            dict: Status and file path of the exported notes.
    """
    try:
        logging.info("Notes generation started...")

        # Validate that at least one of input_content or file_path is provided
        if not (input_content or file_path):
            raise ValueError("Either 'input_content' or 'file_path' must be provided.")
        # Extract content based on input type
        if input_type == 'text' and input_content:
            content = input_content
        elif input_type == 'file' and file_path:
            # This is a check to validate file type before proceeding
            if not file_path.endswith(('.txt', '.docx', '.pdf', '.csv')):
                raise ValueError(f"Unsupported file type for file: {file_path}")
            content = extract_text_from_file(file_path)
            # The below is to clean the extracted text
            content = re.sub(r'[^\x00-\x7F]+', '', content)  # Remove non-ASCII characters
            content = content.replace('\x00', '')  # Remove null bytes
            content = ''.join([char if char.isprintable() else '' for char in content])  # Remove non-printable characters
            
        elif input_type == 'url' and input_content:
            content = extract_text_from_url(input_content)
        else:
            raise ValueError("Invalid input or missing content.")
        
        # Generate notes
        notes = generate_notes(content, focus_topic, output_structure)

        # Export notes
        exported_file_path = export_notes(notes, export_format)

        logging.info("Notes generation completed successfully.")
        return {"status": "success", "file_path": exported_file_path}
    
    except ValueError as ve:
        logging.error(f"ValueError during notes generation: {str(ve)}")
        return {"status": "error", "message": str(ve)}

    except FileNotFoundError as fnf:
        logging.error(f"FileNotFoundError: {str(fnf)}")
        return {"status": "error", "message": "File not found. Please check the file path."}
    
    except Exception as e:
        logging.error(f"Unexpected error during notes generation: {str(e)}")
        return {"status": "error", "message": "An unexpected error occurred. Please try again."}