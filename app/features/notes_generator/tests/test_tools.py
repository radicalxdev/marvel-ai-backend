import os
import pytest
from unittest.mock import patch, MagicMock


from app.features.notes_generator.tools import (
    extract_text_from_file,
    extract_text_from_url,
    generate_notes_rag,
    clean_content
)

"""
If there is an error of file not found while trying to test directly with
pytest test_tools.py, please use:

PYTHONPATH=./ pytest app/features/notes_generator/tests/test_tools.py
"""


def test_extract_text_from_file_pdf():
    """
    Test extracting text from a file that has an unsupported file extension.
    We expect a ValueError if the file extension is not recognized.
    """
    with pytest.raises(ValueError):
        # 'dummy.xyz' is not in the supported file extension list
        extract_text_from_file("dummy.xyz")


def test_extract_text_from_url():
    """
    Test extracting text from a YouTube URL.
    In a real environment, you might want to mock this call to avoid external API usage.
    Here, we assume the YouTubeTranscriptApi returns a transcript containing "make you sleep".
    """
    text = extract_text_from_url("fFlG9waFfJE")  # Example video ID
    # This placeholder assertion checks if "make you sleep" appears in the transcript.
    assert "make you sleep" in text


@patch("app.features.notes_generator.tools.FAISS.from_texts")
@patch("app.features.notes_generator.tools.RetrievalQA.from_chain_type")
def test_generate_notes_rag(mock_retrievalqa, mock_faiss):
    """
    Test the RAG-based note generator function by mocking FAISS and RetrievalQA.
    This ensures we don't make real embeddings or LLM calls.
    """

    # Mock the FAISS vector store
    mock_vectorstore = MagicMock()
    mock_faiss.return_value = mock_vectorstore

    # Mock the QA chain
    mock_qa_chain = MagicMock()
    mock_retrievalqa.return_value = mock_qa_chain

    # Define the return value when calling qa_chain.run(...)
    mock_qa_chain.run.return_value = "Mocked RAG-based summary"

    # Call our generate_notes_rag function
    content = "Mock content for RAG test."
    focus_topic = "Mock Topic"
    structure = "bullet"

    result = generate_notes_rag(content, focus_topic, structure)

    # Verify that FAISS.from_texts was called once
    mock_faiss.assert_called_once()
    # Verify that RetrievalQA.from_chain_type was called
    mock_retrievalqa.assert_called_once()

    # Check the final result
    assert result == "Mocked RAG-based summary"


def test_clean_content():
    """
    Test the clean_content function to ensure it removes
    non-printable or invalid characters.
    """
    raw_text = "Hello\x00 World! \x99"
    cleaned = clean_content(raw_text)
    # '\x00' and '\x99' should be removed
    assert cleaned == "Hello World! "