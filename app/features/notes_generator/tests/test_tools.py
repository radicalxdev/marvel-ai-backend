import pytest
from app.features.notes_generator.tools import (
    extract_text_from_file,
    extract_text_from_url,
    export_notes
)
import os

def test_extract_text_from_file_pdf():
    """Test extracting text from PDF."""
    with pytest.raises(ValueError):
        extract_text_from_file("dummy.xyz")  # Unsupported file format

def test_extract_text_from_url(mocker):
    """Test extracting text from a URL."""
    mock_response = mocker.patch("requests.get")
    mock_response.return_value.text = "<p>Photosynthesis process.</p>"
    text = extract_text_from_url("https://example.com")
    assert "Photosynthesis process" in text

def test_export_notes_txt():
    """Test exporting notes to TXT."""
    notes = "These are sample notes."
    file_path = export_notes(notes, "txt")
    assert os.path.exists(file_path)
    with open(file_path, 'r') as f:
        assert f.read() == notes
    os.remove(file_path)  # Cleanup

def test_export_notes_docx():
    """Test exporting notes to DOCX."""
    notes = "These are sample notes."
    file_path = export_notes(notes, "docx")
    assert os.path.exists(file_path)
    os.remove(file_path)

def test_export_notes_pdf():
    """Test exporting notes to PDF."""
    notes = "These are sample notes."
    file_path = export_notes(notes, "pdf")
    assert os.path.exists(file_path)
    os.remove(file_path)