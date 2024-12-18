import pytest
from app.features.notes_generator.core import executor
from unittest.mock import patch
import re
import logging

def test_executor_text_input_valid():
    """Test executor with valid text input."""
    result = executor(
        input_type='text',
        input_content="Photosynthesis is a process used by plants.",
        focus_topic="Summarize the key steps of photosynthesis",
        output_structure='bullet',
        export_format='txt'
    )
    assert result["status"] == "success"
    assert "file_path" in result


@patch('app.features.notes_generator.tools.extract_text_from_file')
def test_executor_file_input_valid(mock_extract):
    """Test executor with valid file input."""
    mock_extract.return_value = "Plants convert sunlight into energy."
    result = executor(
        input_type='file',
        file_path="dummy.pdf",
        focus_topic="Photosynthesis steps",
        output_structure='paragraph',
        export_format='docx'
    )
    assert result["status"] == "success"
    assert "file_path" in result

def test_executor_missing_input():
    """Test executor with missing inputs."""
    result = executor(input_type='text', input_content=None)
    assert result["status"] == "error"


def test_executor_invalid_file_type():
    """Test executor with unsupported file type."""
    with pytest.raises(ValueError):
        result = executor(
        input_type='file',
        file_path="unsupported.xyz",
        focus_topic="Photosynthesis steps",
        output_structure='paragraph',
        export_format='docx'
    )
        
    assert result["status"] == "success"
    assert "file_path" in result

@patch('app.features.notes_generator.tools.extract_text_from_url')
def test_executor_url_input_valid(mock_extract):
    """Test executor with valid URL input."""
    mock_extract.return_value = "Sunlight absorbed by plants for photosynthesis."
    result = executor(
        input_type='url',
        input_content="fFlG9waFfJE",
        focus_topic="Photosynthesis steps",
        output_structure='table',
        export_format='pdf'
    )
    assert result["status"] == "success"
    assert "file_path" in result
