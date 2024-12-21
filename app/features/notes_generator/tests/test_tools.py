import pytest
import os
from app.features.notes_generator.tools import (
    extract_text_from_file,
    extract_text_from_url,
    export_notes
)

"""if there is an error of file not found while trying to test directly with
    pytest test_tools.py, please use this path👇🏻
    'PYTHONPATH=./ pytest app/features/notes_generator/tests/test_tools.py' """

def test_extract_text_from_file_pdf():
    """Test extracting text from PDF."""
    with pytest.raises(ValueError):
        extract_text_from_file("dummy.xyz")  # Unsupported file format


def test_extract_text_from_url(mocker):
    """Test extracting text from a URL."""
    text = extract_text_from_url("fFlG9waFfJE") 
    """This is a valid youtube video id from (https://www.youtube.com/watch?v=fFlG9waFfJE), 
        you can replace it with any valid youtube video id as seen above and in the test_core.py file
        but make sure to assert the right text from the video transcript, the current assert is just a placeholder
        and the video used has a transcript that says "make you sleep" """
    assert "make you sleep" in text

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