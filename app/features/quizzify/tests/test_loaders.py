import pytest
import json
from unittest.mock import patch, MagicMock
from services.tool_registry import ToolFile
from features.quizzify.tools import (
    URLLoader, 
    BytesFilePDFLoader,
    BytesFileDocxLoader,
    PPTXLoader,
    YouTubeLoader,
    Document
    )  # Adjust the import path as necessary

@pytest.fixture
def pdf_loader():
    return BytesFilePDFLoader

@pytest.fixture
def url_loader(pdf_loader):
    return URLLoader(file_loader=pdf_loader, expected_file_type="pdf")

def test_documents_from_pdf_loader():
    # Arrange the data
    with open('test_documents.json','r') as json_File:
        test_documents=json.load(json_File)
    
    test_url = test_documents['PDF']
    tool_file = []
    tool_file.append(ToolFile(url=test_url, filePath = test_url, filename = "PDF"))

    # Use the loader
    documents = URLLoader.load(tool_file)

    # Assert
    assert isinstance(documents, list)
    assert len(documents) >= 1

def test_documents_from_docx_loader():
    # Arrange the data
    with open('test_documents.json','r') as json_File:
        test_documents=json.load(json_File)
    
    test_url = test_documents['DOCX']
    tool_file = []
    tool_file.append(ToolFile(url=test_url, filePath = test_url, filename = "DOCX"))

    # Use the loader
    documents = URLLoader.load(tool_file)

    # Assert
    assert isinstance(documents, list)
    assert len(documents) >= 1

def test_documents_from_pptx_loader():
    # Arrange the data
    with open('test_documents.json','r') as json_File:
        test_documents=json.load(json_File)
    
    test_url = test_documents['PPTX']
    tool_file = []
    tool_file.append(ToolFile(url=test_url, filePath = test_url, filename = "PPTX"))

    # Use the loader
    documents = URLLoader.load(tool_file)

    # Assert
    assert isinstance(documents, list)
    assert len(documents) >= 1

def test_documents_from_csv_loader():
    # Arrange the data
    with open('test_documents.json','r') as json_File:
        test_documents=json.load(json_File)
    
    test_url = test_documents['CSV']
    tool_file = []
    tool_file.append(ToolFile(url=test_url, filePath = test_url, filename = "CSV"))

    # Use the loader
    documents = URLLoader.load(tool_file)

    # Assert
    assert isinstance(documents, list)
    assert len(documents) >= 1

def test_documents_from_txt_loader():
    # Arrange the data
    with open('test_documents.json','r') as json_File:
        test_documents=json.load(json_File)
    
    test_url = test_documents['TXT']
    tool_file = []
    tool_file.append(ToolFile(url=test_url, filePath = test_url, filename = "TXT"))

    # Use the loader
    documents = URLLoader.load(tool_file)

    # Assert
    assert isinstance(documents, list)
    assert len(documents) >= 1

def test_documents_from_youtube_loader():
    # Arrange the data
    with open('test_documents.json','r') as json_File:
        test_documents=json.load(json_File)
    
    test_url = test_documents['YOUTUBE']
    tool_file = []
    tool_file.append(ToolFile(url=test_url, filePath = test_url, filename = "YOUTUBE"))

    # Use the loader
    documents = URLLoader.load(tool_file)

    # Assert
    assert isinstance(documents, list)
    assert len(documents) >= 1

def test_documents_from_web_loader():
    # Arrange the data
    with open('test_documents.json','r') as json_File:
        test_documents=json.load(json_File)
    
    test_url = test_documents['WEB']
    tool_file = []
    tool_file.append(ToolFile(url=test_url, filePath = test_url, filename = "WEB"))

    # Use the loader
    documents = URLLoader.load(tool_file)

    # Assert
    assert isinstance(documents, list)
    assert len(documents) >= 1

def test_documents_from_multiple_loaders():
    # Arrange the data
    with open('test_documents.json','r') as json_File:
        test_documents=json.load(json_File)
    
    test_url_1 = test_documents['PDF']
    test_url_2 = test_documents['PPTX']
    tool_file = []
    tool_file.append(ToolFile(url=test_url_1, filePath = test_url_1, filename = "PDF"))
    tool_file.append(ToolFile(url=test_url_1, filePath = test_url_1, filename = "PDF"))

    # Use the loader
    documents = URLLoader.load(tool_file)

    # Assert
    assert isinstance(documents, list)
    assert len(documents) >= 1


@patch('requests.get')
def test_load_pdf_from_url(mock_get, url_loader):
    
    pdf_file_path = "features/quizzify/tests/test.pdf"
    
    with open(pdf_file_path, 'rb') as file:
        mock_pdf_content = file.read()
    
    # Mocking the response of requests.get
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = mock_pdf_content
    mock_get.return_value = mock_response

    # The URL you're testing with (doesn't matter in this case since it's mocked)
    test_url = "https://example.com/test.pdf"

    # Assuming your Document class has a simple structure for this example
    expected_document = Document(page_content="Mock PDF Content", metadata={"source": "pdf", "page_number": 1})

    # Run the loader
    documents = url_loader.load([test_url])

    # Verify the results
    assert isinstance(documents, list)
    assert len(documents) == 1

@patch('requests.get')
def test_load_pdf_from_url(mock_get):
    # Simulate reading a local PDF file or use mock PDF content
    pdf_file_path = "features/quizzify/tests/test.pdf"
    with open(pdf_file_path, 'rb') as pdf_file:
        pdf_content = pdf_file.read()

    # Mocking the response of requests.get to simulate downloading the PDF
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = pdf_content
    mock_get.return_value = mock_response

    # The specific URL you want to test with
    test_url = "https://firebasestorage.googleapis.com/v0/b/kai-ai-f63c8.appspot.com/o/uploads%2F510f946e-823f-42d7-b95d-d16925293946-Linear%20Regression%20Stat%20Yale.pdf?alt=media&token=caea86aa-c06b-4cde-9fd0-42962eb72ddd"
    tool_file = ToolFile(url=test_url, filePath = test_url, filename = None)
    
    # Instantiate URLLoader class 
    url_loader_instance = URLLoader(BytesFilePDFLoader, expected_file_type="pdf")

    # Assuming you have a URL loader or similar functionality in your application
    documents = url_loader_instance.load([tool_file])
    
    # Verify the results
    assert isinstance(documents, list)
    assert len(documents) == 1