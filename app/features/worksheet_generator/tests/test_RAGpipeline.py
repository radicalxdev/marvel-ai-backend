import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../')))

import pytest
from unittest.mock import Mock, patch, MagicMock
from app.features.worksheet_generator.tools import read_text_file, RAGRunnable, UploadPDFLoader, BytesFilePDFLoader, LocalFileLoader, URLLoader, RAGpipeline, QuizBuilder, TextOrPDFLoader, QuestionGenerator, QuizQuestion, QuestionChoice, Document, LoaderError


@pytest.fixture
def mock_dependencies():
    loader = MagicMock()
    splitter = MagicMock()
    vectorstore_class = MagicMock()
    embedding_model = MagicMock()
    verbose = False
    
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

    assert rag_pipeline is not None
    assert rag_pipeline.loader == loader
    assert rag_pipeline.splitter == splitter
    assert rag_pipeline.vectorstore_class == vectorstore_class
    assert rag_pipeline.embedding_model == embedding_model
    assert rag_pipeline.verbose == verbose

def test_load_PDFs(mock_dependencies):
    rag_pipeline = mock_dependencies["rag_pipeline"]
    loader = mock_dependencies["loader"]

    files = ["file1.pdf", "file2.pdf"]
    loaded_documents = ["doc1", "doc2"]
    loader.load.return_value = loaded_documents

    result = rag_pipeline.load_PDFs(files)
    loader.load.assert_called_once_with(files)
    assert result == loaded_documents

def test_split_loaded_documents(mock_dependencies):
    rag_pipeline = mock_dependencies["rag_pipeline"]
    splitter = mock_dependencies["splitter"]

    documents = ["doc1", "doc2"]
    split_documents = ["split_doc1", "split_doc2"]
    splitter.split_documents.return_value = split_documents

    result = rag_pipeline.split_loaded_documents(documents)
    splitter.split_documents.assert_called_once_with(documents)
    assert result == split_documents

def test_create_vectorstore(mock_dependencies):
    rag_pipeline = mock_dependencies["rag_pipeline"]
    vectorstore_class = mock_dependencies["vectorstore_class"]
    embedding_model = mock_dependencies["embedding_model"]

    documents = ["doc1", "doc2"]
    vectorstore = MagicMock()
    vectorstore_class.from_documents.return_value = vectorstore

    result = rag_pipeline.create_vectorstore(documents)
    vectorstore_class.from_documents.assert_called_once_with(documents, embedding_model)
    assert result == vectorstore

def test_compile(mock_dependencies):
    rag_pipeline = mock_dependencies["rag_pipeline"]

    try:
        rag_pipeline.compile()
    except Exception as e:
        pytest.fail(f"compile() raised Exception unexpectedly: {e}")

def test_call(mock_dependencies):
    rag_pipeline = mock_dependencies["rag_pipeline"]

    documents = ["doc1", "doc2"]
    loaded_documents = ["loaded_doc1", "loaded_doc2"]
    split_documents = ["split_doc1", "split_doc2"]
    vectorstore = MagicMock()

    # Mocking the methods with chaining support
    with patch.object(rag_pipeline.loader, 'load', return_value=loaded_documents) as mock_load, \
         patch.object(rag_pipeline.splitter, 'split_documents', return_value=split_documents) as mock_split, \
         patch.object(rag_pipeline.vectorstore_class, 'from_documents', return_value=vectorstore) as mock_from_documents:
        
        # Compile the pipeline (this should be done before calling rag_pipeline)
        rag_pipeline.compile()
        
        # Calling the pipeline
        result = rag_pipeline(documents)

        # Assertions
        mock_load.assert_called_once_with(documents)
        mock_split.assert_called_once_with(loaded_documents)
        mock_from_documents.assert_called_once_with(split_documents, rag_pipeline.embedding_model)
        assert result == vectorstore
