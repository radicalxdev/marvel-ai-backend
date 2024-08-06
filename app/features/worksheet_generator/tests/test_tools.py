import os
from dotenv import load_dotenv, find_dotenv
import logging
import pytest
from app.features.worksheet_generator.tools import RAGpipeline, TextOrPDFLoader, UploadPDFLoader, read_text_file
from app.features.worksheet_generator.tools import RAGRunnable
from app.features.worksheet_generator.tools import BytesFilePDFLoader
from unittest.mock import MagicMock, patch
from io import BytesIO
from fastapi import UploadFile
# from PyPDF2 import PdfReader

load_dotenv(find_dotenv())

# default logging setting:
logging.basicConfig(level=logging.INFO)

# Fixture Section

    # Create a mock file, called sample.txt.
@pytest.fixture
def sample_text_file(tmpdir):
    file_path = tmpdir.join("sample.txt")
    file_path.write("This is a test file.")
    return file_path

@pytest.fixture
    # Creating a mock UploadFile object
def mock_upload_file():

    upload_file = MagicMock(spec=UploadFile)
    upload_file.filename = "sample.pdf"
    
    pdf_content = b"%PDF-1.4\n\n1 0 obj\n<< /Type /Catalog /Pages 3 0 R >>\nendobj\n\n2 0 obj\n<< /Type /Page /Parent 3 0 R /Contents 5 0 R >>\nendobj\n\n3 0 obj\n<< /Type /Pages /Kids [2 0 R] /Count 1 >>\nendobj\n\n4 0 obj\n<< /Title (Sample Document) /Creator (Me) /Producer (My PDF Library 1.0) >>\nendobj\n\n5 0 obj\n<< /Length 20 >>\nstream\n0.2 0.2 0.2 rg\nBT\n/F1 12 Tf\n72 712 Td\n(Hello World) Tj\nET\nendstream\nendobj\n\n6 0 obj\n<< /Type /Font /Subtype /Type1 /Name /F1 /BaseFont /Times-Roman >>\nendobj\n\nxref\n0 7\n0000000000 65535 f \n0000000009 00000 n \n0000000054 00000 n \n0000000102 00000 n \n0000000174 00000 n \n0000000275 00000 n \n0000000354 00000 n \ntrailer\n<< /Size 7 /Root 1 0 R >>\nstartxref\n460\n%%EOF\n"
    file_stream = BytesIO(pdf_content)
    file_stream.name = "sample.pdf"  # Setting a name attribute as well
    upload_file.file = file_stream
    
    return upload_file
    
    # Reason: ?
@pytest.fixture
def mock_pdf_bytes():
    pdf_content = b"%PDF-1.4\n\n1 0 obj\n<< /Type /Catalog /Pages 3 0 R >>\nendobj\n\n2 0 obj\n<< /Type /Page /Parent 3 0 R /Contents 5 0 R >>\nendobj\n\n3 0 obj\n<< /Type /Pages /Kids [2 0 R] /Count 1 >>\nendobj\n\n4 0 obj\n<< /Title (Sample Document) /Creator (Me) /Producer (My PDF Library 1.0) >>\nendobj\n\n5 0 obj\n<< /Length 20 >>\nstream\n0.2 0.2 0.2 rg\nBT\n/F1 12 Tf\n72 712 Td\n(Hello World) Tj\nET\nendstream\nendobj\n\n6 0 obj\n<< /Type /Font /Subtype /Type1 /Name /F1 /BaseFont /Times-Roman >>\nendobj\n\nxref\n0 7\n0000000000 65535 f \n0000000009 00000 n \n0000000054 00000 n \n0000000102 00000 n \n0000000174 00000 n \n0000000275 00000 n \n0000000354 00000 n \ntrailer\n<< /Size 7 /Root 1 0 R >>\nstartxref\n460\n%%EOF\n"
    return BytesIO(pdf_content)
    
    # Reason: ?
@pytest.fixture
def mock_pdf_file(tmpdir):
    # Creating a temporary PDF file
    file_path = tmpdir.join("sample.pdf")
    file_path.write(b"%PDF-1.4\n\n1 0 obj\n<< /Type /Catalog /Pages 3 0 R >>\nendobj\n\n2 0 obj\n<< /Type /Page /Parent 3 0 R /Contents 5 0 R >>\nendobj\n\n3 0 obj\n<< /Type /Pages /Kids [2 0 R] /Count 1 >>\nendobj\n\n4 0 obj\n<< /Title (Sample Document) /Creator (Me) /Producer (My PDF Library 1.0) >>\nendobj\n\n5 0 obj\n<< /Length 20 >>\nstream\n0.2 0.2 0.2 rg\nBT\n/F1 12 Tf\n72 712 Td\n(Hello World) Tj\nET\nendstream\nendobj\n\n6 0 obj\n<< /Type /Font /Subtype /Type1 /Name /F1 /BaseFont /Times-Roman >>\nendobj\n\nxref\n0 7\n0000000000 65535 f \n0000000009 00000 n \n0000000054 00000 n \n0000000102 00000 n \n0000000174 00000 n \n0000000275 00000 n \n0000000354 00000 n \ntrailer\n<< /Size 7 /Root 1 0 R >>\nstartxref\n460\n%%EOF\n")
    return file_path

    # Reason: ?
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
    
    # Reason: ?
@pytest.fixture
def mock_upload_file():
    # Mock UploadFile object with file content
    return MockUploadFile(["Page 1 content", "Page 2 content"])


# Patch Section

# Reason: ??????????????
class MockPdfPage:
    def extract_text(self):
        return "Hello World"

# Reason: ??????????????

class MockPdfReader:
    def __init__(self, file):
        self.pages = [MockPdfPage()]

# Reason: ??????????????
@patch('app.features.worksheet_generator.tools.PdfReader', new=MockPdfReader)
def test_bytes_file_pdf_loader_valid_pdf(mock_pdf_bytes):
    # Creating an instance of BytesFilePDFLoader with a valid PDF file
    files = [(mock_pdf_bytes, "pdf")]
    pdf_loader = BytesFilePDFLoader(files)
    
    documents = pdf_loader.load()
    
    
    assert isinstance(documents, list)
    assert len(documents) == 1
    assert documents[0].metadata["source"] == "pdf"
    assert documents[0].metadata["page_number"] == 1
    assert documents[0].page_content.strip() == "Hello World"


# Reason: ?????????????? Please explain why you want to do this test?
# @patch('app.features.worksheet_generator.tools.PdfReader', new=MockPdfReader)
# def test_local_file_loader_valid_pdf(mock_pdf_file):
#     Creating an instance of LocalFileLoader with a valid PDF file
#     file_path = str(mock_pdf_file)
#     loader = LocalFileLoader([file_path])

#     documents = loader.load()

#     assert isinstance(documents, list)
#     assert len(documents) == 1
#     assert documents[0].metadata["source"] == file_path
#     assert documents[0].metadata["page_number"] == 1
#     assert documents[0].page_content.strip() == "Hello World"



# Test Cases:

# 1st Test Cases: function of "read_text_file" in tool.py
def test_read_text_file(sample_text_file):
    # absolute path of the sample file
    file_path = os.path.abspath(sample_text_file)

    # Call the function
    content = read_text_file(file_path)

    # Print the result
    logging.info(f"This is a test file and the testing is successful.")

    # Verify the function output
    assert content == "This is a test file."
    
    
# 2nd Test Cases:
def test_ragrunnable_call():
    def sample_func(x):
        return x + 1
    
    runnable = RAGRunnable(sample_func)

    result = runnable(5)
    assert result == 6


# Reason: ???? Which class??? 
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


# Reason: ???? Which class??? 
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


# Reason: ???? Which class??? 
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



# Reason: ???? Which class??? 
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


# Reason: ???? Which class??? 
class MockUploadFile:
    def __init__(self, file_content):
        self.file_content = file_content
        self.file = MagicMock()
        self.file.__enter__.return_value.read.side_effect = self.read_file

    def read_file(self):
        for content in self.file_content:
            yield content.encode('utf-8')

# Reason: ???? Which class??? 
def test_load_with_text():
    loader = TextOrPDFLoader(text="Sample text")
    result = loader.load()
    assert result == "Sample text"

# Reason: ???? Which class??? 
def test_load_with_pdf(mock_upload_file, monkeypatch):
    loader = TextOrPDFLoader(file=mock_upload_file.file)
    
    # Mock PdfReader to return content from mock file
    pdf_reader_mock = MagicMock()
    pdf_reader_mock.pages = [
        MagicMock(extract_text=lambda: "Page 1 content"),
        MagicMock(extract_text=lambda: "Page 2 content")
    ]
    monkeypatch.setattr('app.features.worksheet_generator.tools.PdfReader', lambda x: pdf_reader_mock)
    
    result = loader.load()
    assert "Page 1 content" in result
    assert "Page 2 content" in result


# Reason: ???? Which class??? 
def test_load_without_text_or_file():
    loader = TextOrPDFLoader()
    with pytest.raises(ValueError, match="No text or file provided for question generation"):
        loader.load()