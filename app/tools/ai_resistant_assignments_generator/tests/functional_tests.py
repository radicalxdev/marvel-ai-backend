import pytest
from langchain_core.documents import Document
from app.tools.ai_resistant_assignments_generator.tools import (
    AIResistantAssignmentGenerator,
    read_text_file
)
from app.services.schemas import AIResistantArgs
from langchain_chroma import Chroma
from pydantic import ValidationError


# ==================== Correct Cases ====================

# Test read_text_file with valid input
def test_read_text_file_correct_case(mocker):
    mocker.patch('os.path.join', return_value="dummy_path.txt")
    mock_open = mocker.patch('builtins.open', mocker.mock_open(read_data="Sample prompt content"))

    result = read_text_file("dummy_path.txt")

    assert result == "Sample prompt content"
    mock_open.assert_called_once_with("dummy_path.txt", 'r')


# Test AIResistantAssignmentGenerator initialization
def test_ai_resistant_assignments_generator_initialization_correct():
    args = AIResistantArgs(
        assignment="Sample Assignment",
        grade_level="elementary",
        file_type="pdf",
        file_url="http://example.com/test.pdf",
        lang="en"
    )
    generator = AIResistantAssignmentGenerator(args=args, vectorstore_class=Chroma, verbose=True)

    assert generator.args.assignment == "Sample Assignment"
    assert generator.args.grade_level == "elementary"
    assert generator.verbose is True
    assert generator.vectorstore is None


# Test compile_with_docs creates chain with valid documents
def test_compile_with_docs_correct_case(mocker):
    mock_documents = [Document(page_content="Test content", metadata={"page": 1})]

    mock_vectorstore = mocker.MagicMock()
    mock_vectorstore.as_retriever.return_value = mocker.MagicMock()
    mocker.patch('langchain_chroma.Chroma.from_documents', return_value=mock_vectorstore)

    args = AIResistantArgs(
        assignment="Test Assignment",
        grade_level="elementary",
        file_type="pdf",
        file_url="http://example.com/test.pdf",
        lang="en"
    )
    generator = AIResistantAssignmentGenerator(args=args, verbose=True)
    chain = generator.compile_with_docs(mock_documents)

    assert generator.vectorstore == mock_vectorstore
    assert chain is not None


# ==================== Incorrect Cases ====================

# Test read_text_file with invalid path
def test_read_text_file_invalid_case(mocker):
    mocker.patch('os.path.join', return_value="invalid_path.txt")
    mocker.patch('builtins.open', side_effect=FileNotFoundError)

    with pytest.raises(FileNotFoundError):
        read_text_file("invalid_path.txt")


# Test AIResistantAssignmentGenerator initialization with missing assignment
def test_ai_resistant_assignments_generator_missing_assignment():
    with pytest.raises(ValidationError):
        AIResistantAssignmentGenerator(args=AIResistantArgs(
            assignment=None,
            grade_level="elementary",
            file_type="pdf",
            file_url="http://example.com/test.pdf",
            lang="en"
        ))


# Test compile_with_docs with missing documents
def test_compile_with_docs_missing_documents(mocker):
    mock_vectorstore = mocker.MagicMock()
    mock_vectorstore.as_retriever.return_value = mocker.MagicMock()
    mocker.patch('langchain_chroma.Chroma.from_documents', return_value=mock_vectorstore)

    args = AIResistantArgs(
        assignment="Test Assignment",
        grade_level="elementary",
        file_type="pdf",
        file_url="http://example.com/test.pdf",
        lang="en"
    )
    generator = AIResistantAssignmentGenerator(args=args, verbose=True)

    chain = generator.compile_with_docs([])
    assert generator.vectorstore == mock_vectorstore
    assert chain is not None

# ==================== Edge Cases ====================

# Test compile_with_docs with empty documents
def test_compile_with_docs_empty_documents(mocker):
    mock_documents = []

    mock_vectorstore = mocker.MagicMock()
    mock_vectorstore.as_retriever.return_value = mocker.MagicMock()
    mocker.patch('langchain_chroma.Chroma.from_documents', return_value=mock_vectorstore)

    args = AIResistantArgs(
        assignment="Edge Case Assignment",
        grade_level="elementary",
        file_type="pdf",
        file_url="http://example.com/test.pdf",
        lang="en"
    )
    generator = AIResistantAssignmentGenerator(args=args, verbose=True)
    chain = generator.compile_with_docs(mock_documents)

    assert generator.vectorstore == mock_vectorstore
    assert chain is not None

# Test create_assignments without documents
def test_create_assignments_without_documents(mocker):
    mock_chain = mocker.MagicMock()
    mock_chain.invoke.return_value = {"result": "Generated assignment"}
    mocker.patch(
        'app.tools.ai_resistant_assignments_generator.tools.AIResistantAssignmentGenerator.compile_without_docs',
        return_value=mock_chain
    )

    args = AIResistantArgs(
        assignment="Edge Case Assignment",
        grade_level="elementary",
        file_type="pdf",
        file_url="http://example.com/test.pdf",
        lang="en"
    )
    generator = AIResistantAssignmentGenerator(args=args, verbose=True)
    result = generator.create_assignments(None)

    assert result == {"result": "Generated assignment"}
    mock_chain.invoke.assert_called_once()


# Test AIResistantAssignmentGenerator with unsupported language
def test_ai_resistant_assignments_generator_unsupported_language(mocker):
    with pytest.raises(ValidationError, match="Input should be a valid string"):
        AIResistantAssignmentGenerator(args=AIResistantArgs(
            assignment="Unsupported Language Assignment",
            grade_level="elementary",
            file_type="pdf",
            file_url="http://example.com/test.pdf",
            lang=123
        ))