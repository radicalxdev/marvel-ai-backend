import sys
import os

# Add the root directory to the sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from app.features.text_rewriter.tools import process_text, process_file

def test_process_text():
    text = "Romeo and Juliet is a tragic play by William Shakespeare."
    instruction = "simplify"
    result = process_text(text, instruction)
    assert result is not None  # Adjust based on actual logic

def test_process_file():
    file_data = {"file_content": "Some file content"}
    instruction = "simplify"
    result = process_file(file_data, instruction)
    assert result == "Processed file content"  # Adjust based on actual logic