from typing import Union, Dict, Any
import logging
from .tools import process_text, process_file
from langchain import LangChain

logging.basicConfig(level=logging.INFO)

def executor(input_data: Union[str, Dict[str, Any]], instruction: str) -> str:
    """
    Main function to rewrite text based on the provided instruction.
    """
    try:
        if isinstance(input_data, str):
            return process_text(input_data, instruction)
        elif isinstance(input_data, dict):
            return process_file(input_data, instruction)
        else:
            raise ValueError("Invalid input data type")
    except Exception as e:
        logging.error(f"Error in executor: {e}")
        raise