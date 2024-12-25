import re
from typing import Literal, Optional, Dict
import logging
from tools import (
    extract_text_from_file,
    extract_text_from_url,
    generate_notes_rag,
    clean_content
)

# Dictionary to map input types to corresponding functions
file_handler_map = {
    'text': lambda content: clean_content(content),  # Clean content directly
    'file': extract_text_from_file,
    'url': extract_text_from_url
}

# List of supported file extensions
SUPPORTED_FILE_TYPES = ['.txt', '.docx', '.pdf', '.csv', '.pptx', '.md', '.xml', '.xls', '.xlsx']

def executor(input_type: Literal['text', 'file', 'url'],
             input_content: Optional[str] = None,
             file_path: Optional[str] = None,
             focus_topic: Optional[str] = None,
             output_structure: Literal['bullet', 'paragraph', 'table'] = 'bullet',
             export_format: Literal['json'] = 'json') -> Dict[str, str]:
    try:
        logging.info("Notes generation started...")

        # Validate that at least one of input_content or file_path is provided
        if not (input_content or file_path):
            raise ValueError("Either 'input_content' or 'file_path' must be provided.")

        # Validate the file type if file_path is provided
        if file_path and not any(file_path.endswith(ext) for ext in SUPPORTED_FILE_TYPES):
            raise ValueError(f"Unsupported file type for file: {file_path}")

        # Extract content based on input type
        if input_type in file_handler_map:
            if input_type == 'text' and input_content:
                content = file_handler_map[input_type](input_content)
            elif input_type == 'file' and file_path:
                content = file_handler_map[input_type](file_path)
            elif input_type == 'url' and input_content:
                content = file_handler_map[input_type](input_content)
        else:
            raise ValueError("Invalid input type or missing content.")
        
        # Generate notes
        notes = generate_notes_rag(content, focus_topic, output_structure)
        
        # Return the generated notes (No export logic)
        logging.info("Notes generation completed successfully.")
        return {"status": "success", "notes": notes}
    
    except ValueError as ve:
        logging.error(f"ValueError during notes generation: {str(ve)}")
        return {"status": "error", "message": str(ve)}
    except FileNotFoundError as fnf:
        logging.error(f"FileNotFoundError: {str(fnf)}")
        return {"status": "error", "message": "File not found. Please check the file path."}
    except Exception as e:
        logging.error(f"Unexpected error during notes generation: {str(e)}")
        return {"status": "error", "message": "An unexpected error occurred. Please try again."}
