from app.features.notes_generator.tools import process_text, process_file

def test_process_text():
    text = "Photosynthesis is a process used by plants to convert sunlight into energy."
    result = process_text(text)
    assert result == text  # Adjust based on actual logic

def test_process_file():
    file_content = b"Some file content"
    result = process_file(file_content)
    assert result == "Extracted content from the file."  # Adjust based on actual logic