import os
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
             focus_topic: Optional[str] =  None,
             output_structure: Literal['bullet', 'paragraph', 'table'] = 'bullet',
             export_format: Literal['txt', 'docx', 'pdf'] = 'txt') -> Dict:
    print("Current working directory:", os.getcwd())
    
    """
    Main executor function for Notes Genrator Tool.
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

        # Extrat content
        if input_type == 'text' and input_content:
            content = input_content
        elif input_type == 'file' and file_path:
            # Add a check to validate file type before proceeding
            if not file_path.endswith(('.txt', '.docx', '.pdf')):
                raise ValueError(f"Unsupported file type for file: {file_path}")
            content = extract_text_from_file(file_path)
            
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
    except Exception as e:
        logging.error(f"Error during notes generation: {str(e)}")
        return {"status": "error", "messsage": str(e)}
