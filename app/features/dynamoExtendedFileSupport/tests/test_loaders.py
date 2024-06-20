import pytest
import requests
from unittest.mock import patch, MagicMock
from features.dynamoExtendedFileSupport.tools import load_pdf_documents, load_csv_documents, load_txt_documents, load_md_documents, load_url_documents
from api.error_utilities import FileHandlerError

def test_load_pdf_documents_valid():
    pdf_url = "https://gbihr.org/images/docs/test.pdf"
    pages = load_pdf_documents(pdf_url)
    assert isinstance(pages, list)
    assert len(pages) > 0

def test_load_pdf_documents_invalid():
    dummy_pdf_url = "https://gbihr.org/images/docs/dummy.pdf"

    with pytest.raises(requests.exceptions.HTTPError) as exc_info:
        pages = load_pdf_documents(dummy_pdf_url)

    assert isinstance(exc_info.value, requests.exceptions.HTTPError)
    assert exc_info.value.response.status_code == 404

def test_load_pdf_documents_invalid_file_type():
    not_pdf_url = "https://github.com/AaronSosaRamos/kai-ai-backend/blob/epic-7.2-imp/README.md"

    with pytest.raises(FileHandlerError) as exc_info:
        pages = load_pdf_documents(not_pdf_url)

    assert isinstance(exc_info.value, FileHandlerError)

def test_load_csv_documents_valid():
    csv_url = "https://github.com/ShapeLab/ZooidsCompositePhysicalizations/blob/master/Zooid_Vis/bin/data/student-dataset.csv"
    pages = load_csv_documents(csv_url)
    assert isinstance(pages, list)
    assert len(pages) > 0

def test_load_csv_documents_invalid():
    dummy_csv_url = "https://people.sc.fsu.edu/~jburkardt/data/csv/dummy.csv"

    with pytest.raises(requests.exceptions.HTTPError) as exc_info:
        pages = load_csv_documents(dummy_csv_url)

    assert isinstance(exc_info.value, requests.exceptions.HTTPError)
    assert exc_info.value.response.status_code == 404 

def test_load_csv_documents_invalid_file_type():
    not_csv_url = "https://gbihr.org/images/docs/test.pdf"

    with pytest.raises(FileHandlerError) as exc_info:
        pages = load_csv_documents(not_csv_url)

    assert isinstance(exc_info.value, FileHandlerError)

def test_load_txt_documents_valid():
    txt_url = "https://example-files.online-convert.com/document/txt/example.txt"
    pages = load_txt_documents(txt_url)
    assert isinstance(pages, list)
    assert len(pages) > 0

def test_load_txt_documents_invalid():
    dummy_txt_url = "https://example-files.online-convert.com/document/txt/dummy.txt"

    with pytest.raises(requests.exceptions.HTTPError) as exc_info:
        pages = load_txt_documents(dummy_txt_url)

    assert isinstance(exc_info.value, requests.exceptions.HTTPError)
    assert exc_info.value.response.status_code == 404

def test_load_txt_documents_invalid_file_type():
    not_txt_url = "https://gbihr.org/images/docs/test.pdf"

    with pytest.raises(FileHandlerError) as exc_info:
        pages = load_txt_documents(not_txt_url)

    assert isinstance(exc_info.value, FileHandlerError)

def test_load_md_documents_valid():
    md_url = "https://github.com/AaronSosaRamos/kai-ai-backend/blob/epic-7.2-imp/README.md"
    pages = load_md_documents(md_url)
    assert isinstance(pages, list)
    assert len(pages) > 0

def test_load_md_documents_invalid():
    dummy_md_url = "https://github.com/AaronSosaRamos/kai-ai-backend/blob/epic-7.2-imp/dummy.md"

    with pytest.raises(requests.exceptions.HTTPError) as exc_info:
        pages = load_md_documents(dummy_md_url)

    assert isinstance(exc_info.value, requests.exceptions.HTTPError)
    assert exc_info.value.response.status_code == 404

def test_load_md_documents_invalid_file_type():
    not_md_url = "https://gbihr.org/images/docs/test.pdf"

    with pytest.raises(FileHandlerError) as exc_info:
        pages = load_md_documents(not_md_url)

    assert isinstance(exc_info.value, FileHandlerError)

def test_load_url_documents_valid():
    valid_url = "https://en.wikipedia.org/wiki/Gemini_(language_model)"
    pages = load_url_documents(valid_url)
    assert isinstance(pages, list)
    assert len(pages) > 0
