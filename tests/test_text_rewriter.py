import pytest
from app.features.text_rewriter.core import (
    rewrite_text,
    simplify_text,
    summarize_text,
    rephrase_text,
    process_file_input,
)
from unittest.mock import patch

import pytest
from app.features.text_rewriter.core import process_url_input



def test_simplify_text():
    input_text = "This is a complex sentence with multiple clauses."
    expected_output = "Simplified text output"  # Replace this based on Gemini output.

    with patch("app.features.text_rewriter.core.initialize_model") as mock_model:
        mock_model.return_value.generate_content.return_value.text = expected_output
        result = simplify_text(input_text)
        assert result == expected_output


def test_summarize_text():
    input_text = "This is a detailed text with multiple points. It provides explanations and examples."
    expected_output = "Summarized text output"  # Replace based on Gemini output.

    with patch("app.features.text_rewriter.core.initialize_model") as mock_model:
        mock_model.return_value.generate_content.return_value.text = expected_output
        result = summarize_text(input_text)
        assert result == expected_output


def test_rephrase_text():
    input_text = "This is an example text for rephrasing."
    expected_output = "Rephrased text output"  # Replace based on Gemini output.

    with patch("app.features.text_rewriter.core.initialize_model") as mock_model:
        mock_model.return_value.generate_content.return_value.text = expected_output
        result = rephrase_text(input_text)
        assert result == expected_output


def test_process_file_input_txt(tmp_path):
    file_path = tmp_path / "test.txt"
    file_path.write_text("This is a sample text file.")

    file_data = {"format": "txt", "path": str(file_path)}
    result = process_file_input(file_data)
    assert result == "This is a sample text file."


def test_process_file_input_csv(tmp_path):
    file_path = tmp_path / "test.csv"
    file_path.write_text("col1,col2\nval1,val2")

    file_data = {"format": "csv", "path": str(file_path)}
    result = process_file_input(file_data)
    assert "col1 col2" in result
    assert "val1 val2" in result

def test_process_url_input():
    url = "https://www.gutenberg.org/cache/epub/84/pg84.txt"  # New working URL
    result = process_url_input(url)
    assert len(result) > 0  # Ensure content is fetched
    assert "Frankenstein" in result  # Validate expected content


def test_invalid_url():
    url = "invalid-url"  # Clearly invalid format
    with pytest.raises(ValueError, match="Invalid URL format."):
        process_url_input(url)

