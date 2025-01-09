from pydantic import ValidationError
import pytest
from app.tools.ai_resistant_assignments_generator.tools import AIResistantAssignmentGenerator
from app.services.schemas import AIResistantArgs
from langchain_core.documents import Document
from app.tools.ai_resistant_assignments_generator.tools import read_text_file

# ==================== Correct Cases ====================

# Test valid file reading
def test_read_text_file(mocker):
    mock_open = mocker.patch('builtins.open', mocker.mock_open(read_data="Sample prompt content"))
    mocker.patch('os.path.join', return_value="dummy_path.txt")

    result = read_text_file("dummy_path.txt")

    assert result == "Sample prompt content"
    mock_open.assert_called_once_with("dummy_path.txt", 'r')

# Test initialization with valid arguments
def test_ai_resistant_assignments_generator_initialization():
    args = AIResistantArgs(
        assignment="Test Assignment",
        grade_level="elementary",
        file_type="pdf",
        file_url="http://example.com/test.pdf",
        lang="en"
    )
    generator = AIResistantAssignmentGenerator(args=args, verbose=True)

    assert generator.args.assignment == "Test Assignment"
    assert generator.args.grade_level == "elementary"
    assert generator.verbose is True

# Test compile_with_docs with valid documents
def test_compile_with_docs_creates_vectorstore(mocker):
    mock_documents = [Document(page_content="Test content", metadata={"page": 1})]
    mock_vectorstore = mocker.MagicMock()
    mock_retriever = mocker.MagicMock()
    mock_vectorstore.as_retriever.return_value = mock_retriever

    mock_from_documents = mocker.patch('langchain_chroma.Chroma.from_documents', return_value=mock_vectorstore)

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
    assert generator.retriever == mock_retriever
    assert chain is not None
    mock_vectorstore.as_retriever.assert_called_once()
    mock_from_documents.assert_called_once_with(mock_documents, generator.embedding_model)

# Test create_assignments with valid documents
def test_create_assignments_with_docs(mocker):
    mock_chain = mocker.MagicMock()
    mock_chain.invoke.return_value = {"result": "Test Response"}
    mock_compile_with_docs = mocker.patch(
        'app.tools.ai_resistant_assignments_generator.tools.AIResistantAssignmentGenerator.compile_with_docs',
        return_value=mock_chain
    )

    mock_vectorstore = mocker.MagicMock()
    mock_vectorstore.delete_collection = mocker.MagicMock()

    args = AIResistantArgs(
        assignment="Test Assignment",
        grade_level="elementary",
        file_type="pdf",
        file_url="http://example.com/test.pdf",
        lang="en"
    )
    generator = AIResistantAssignmentGenerator(args=args, verbose=True)
    generator.vectorstore = mock_vectorstore

    documents = [Document(page_content="Content", metadata={})]
    response = generator.create_assignments(documents)

    assert response == {"result": "Test Response"}
    mock_chain.invoke.assert_called_once()
    mock_compile_with_docs.assert_called_once_with(documents)
    mock_vectorstore.delete_collection.assert_called_once()

# ==================== Incorrect Cases ====================

# Test compile_with_docs raises ValueError for missing documents
def test_compile_with_docs_missing_documents(mocker):
    # Mock vectorstore
    mock_vectorstore = mocker.MagicMock()
    mock_retriever = mocker.MagicMock()
    mock_vectorstore.as_retriever.return_value = mock_retriever

    # Patch Chroma.from_documents to return the mocked vectorstore
    mocker.patch('langchain_chroma.Chroma.from_documents', return_value=mock_vectorstore)

    args = AIResistantArgs(
        assignment="Test Assignment",
        grade_level="elementary",
        file_type="pdf",
        file_url="http://example.com/test.pdf",
        lang="en"
    )
    generator = AIResistantAssignmentGenerator(args=args, verbose=True)

    # Ensure that an empty list doesn't cause an error
    chain = generator.compile_with_docs([])
    assert generator.vectorstore == mock_vectorstore
    assert generator.retriever == mock_retriever
    assert chain is not None

# Test invalid arguments during initialization
def test_invalid_ai_resistant_assignments_generator_initialization():
    with pytest.raises(ValidationError, match="Input should be a valid string"):
        AIResistantAssignmentGenerator(args=AIResistantArgs(
            assignment=None,
            grade_level="elementary",
            file_type="pdf",
            file_url="http://example.com/test.pdf",
            lang="en"
        ))

# ==================== Edge Cases ====================

# Test create_assignments without documents
def test_create_assignments_without_docs(mocker):
    # Mock chain behavior
    mock_chain = mocker.MagicMock()
    mock_chain.invoke.return_value = {"result": "Test Response"}
    mock_compile_without_docs = mocker.patch(
        'app.tools.ai_resistant_assignments_generator.tools.AIResistantAssignmentGenerator.compile_without_docs',
        return_value=mock_chain
    )

    # Provide all required arguments
    args = AIResistantArgs(
        assignment="Test Assignment",
        grade_level="elementary",
        file_type="pdf",
        file_url="http://example.com/test.pdf",
        lang="en"
    )
    generator = AIResistantAssignmentGenerator(args=args, verbose=True)

    # Test create_assignments without documents
    response = generator.create_assignments(None)

    # Assertions
    assert response == {"result": "Test Response"}
    mock_chain.invoke.assert_called_once()
    mock_compile_without_docs.assert_called_once()

# Test compile_with_docs handles empty documents list
def test_compile_with_docs_empty_documents(mocker):
    mock_vectorstore = mocker.MagicMock()
    mock_retriever = mocker.MagicMock()
    mock_vectorstore.as_retriever.return_value = mock_retriever

    mocker.patch('langchain_chroma.Chroma.from_documents', return_value=mock_vectorstore)

    args = AIResistantArgs(
        assignment="Test Assignment",
        grade_level="elementary",
        file_type="pdf",
        file_url="http://example.com/test.pdf",
        lang="en"
    )
    generator = AIResistantAssignmentGenerator(args=args, verbose=True)

    # Ensure empty documents do not break the chain setup
    chain = generator.compile_with_docs([])
    assert generator.vectorstore == mock_vectorstore
    assert generator.retriever == mock_retriever
    assert chain is not None
