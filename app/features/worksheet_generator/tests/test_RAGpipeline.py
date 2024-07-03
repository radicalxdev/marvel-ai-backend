import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../')))

import pytest
from unittest.mock import Mock, patch, MagicMock
from app.features.worksheet_generator.tools import read_text_file, RAGRunnable, UploadPDFLoader, BytesFilePDFLoader, LocalFileLoader, URLLoader, RAGpipeline, QuizBuilder, TextOrPDFLoader, QuestionGenerator, QuizQuestion, QuestionChoice, Document, LoaderError

from langchain_core.documents import Document

@pytest.fixture
def mock_dependencies():
    # Setup mock objects
    loader = MagicMock(spec=UploadPDFLoader)
    splitter = MagicMock()
    vectorstore_class = MagicMock()
    embedding_model = MagicMock()
    verbose = False
    
    # Initialize RAGpipeline with mocks
    rag_pipeline = RAGpipeline(
        loader=loader,
        splitter=splitter,
        vectorstore_class=vectorstore_class,
        embedding_model=embedding_model,
        verbose=verbose
    )
    
    return {
        "loader": loader,
        "splitter": splitter,
        "vectorstore_class": vectorstore_class,
        "embedding_model": embedding_model,
        "verbose": verbose,
        "rag_pipeline": rag_pipeline
    }

def test_initialization(mock_dependencies):
    rag_pipeline = mock_dependencies["rag_pipeline"]
    loader = mock_dependencies["loader"]
    splitter = mock_dependencies["splitter"]
    vectorstore_class = mock_dependencies["vectorstore_class"]
    embedding_model = mock_dependencies["embedding_model"]
    verbose = mock_dependencies["verbose"]

    # Test initialization
    assert rag_pipeline is not None
    assert rag_pipeline.loader == loader
    assert rag_pipeline.splitter == splitter
    assert rag_pipeline.vectorstore_class == vectorstore_class
    assert rag_pipeline.embedding_model == embedding_model
    assert rag_pipeline.verbose == verbose

def test_load_PDFs(mock_dependencies):
    rag_pipeline = mock_dependencies["rag_pipeline"]
    loader = mock_dependencies["loader"]

    # Mock files
    files = ["file1.pdf", "file2.pdf"]
    loaded_documents = ["doc1", "doc2"]
    loader.load.return_value = loaded_documents

    # Test load_PDFs method
    result = rag_pipeline.load_PDFs(files)
    loader.load.assert_called_once_with(files)
    assert result == loaded_documents

def test_split_loaded_documents(mock_dependencies):
    rag_pipeline = mock_dependencies["rag_pipeline"]
    splitter = mock_dependencies["splitter"]

    # Mock documents
    documents = ["doc1", "doc2"]
    split_documents = ["split_doc1", "split_doc2"]
    splitter.split_documents.return_value = split_documents

    # Test split_loaded_documents method
    result = rag_pipeline.split_loaded_documents(documents)
    splitter.split_documents.assert_called_once_with(documents)
    assert result == split_documents

def test_create_vectorstore(mock_dependencies):
    rag_pipeline = mock_dependencies["rag_pipeline"]
    vectorstore_class = mock_dependencies["vectorstore_class"]
    embedding_model = mock_dependencies["embedding_model"]

    # Mock documents
    documents = ["doc1", "doc2"]
    vectorstore = MagicMock()
    vectorstore_class.from_documents.return_value = vectorstore

    # Test create_vectorstore method
    result = rag_pipeline.create_vectorstore(documents)
    vectorstore_class.from_documents.assert_called_once_with(documents, embedding_model)
    assert result == vectorstore

def test_compile(mock_dependencies):
    rag_pipeline = mock_dependencies["rag_pipeline"]

    # Test compile method (ensuring it runs without errors)
    try:
        rag_pipeline.compile()
    except Exception as e:
        pytest.fail(f"compile() raised Exception unexpectedly: {e}")

def test_call(mock_dependencies):
    rag_pipeline = mock_dependencies["rag_pipeline"]

    # Mock documents
    documents = ["doc1", "doc2"]
    loaded_documents = ["loaded_doc1", "loaded_doc2"]
    split_documents = ["split_doc1", "split_doc2"]
    vectorstore = MagicMock()

    # Mock methods
    rag_pipeline.load_PDFs = MagicMock(return_value=loaded_documents)
    rag_pipeline.split_loaded_documents = MagicMock(return_value=split_documents)
    rag_pipeline.create_vectorstore = MagicMock(return_value=vectorstore)

    # Print statements to debug the calls
    print(f"Before __call__: {rag_pipeline.load_PDFs.mock_calls}")
    print(f"Before __call__: {rag_pipeline.split_loaded_documents.mock_calls}")
    print(f"Before __call__: {rag_pipeline.create_vectorstore.mock_calls}")

    # Test __call__ method
    result = rag_pipeline(documents)

    # Print statements to debug the calls
    print(f"After __call__: {rag_pipeline.load_PDFs.mock_calls}")
    print(f"After __call__: {rag_pipeline.split_loaded_documents.mock_calls}")
    print(f"After __call__: {rag_pipeline.create_vectorstore.mock_calls}")

    rag_pipeline.load_PDFs.assert_called_once_with(documents)
    rag_pipeline.split_loaded_documents.assert_called_once_with(loaded_documents)
    rag_pipeline.create_vectorstore.assert_called_once_with(split_documents)
    assert result == vectorstore