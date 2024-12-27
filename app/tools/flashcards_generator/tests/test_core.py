import pytest
from app.tools.flashcards_generator.core import executor

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

# PDF Tests
def test_executor_pdf_url_valid():
    flashcards = executor(
        file_url="https://filesamples.com/samples/document/pdf/sample1.pdf",
        file_type="pdf",
        lang="en"
    )
    assert isinstance(flashcards, list)

def test_executor_pdf_url_invalid():
    with pytest.raises(ValueError) as exc_info:
        executor(
            file_url="https://filesamples.com/samples/document/pdf/sample1.pdf",
            file_type=1,
            lang="en"
        )
    assert isinstance(exc_info.value, ValueError)

# CSV Tests
def test_executor_csv_url_valid():
    quiz = executor(
        file_url="https://filesamples.com/samples/document/csv/sample1.csv",
        file_type="csv",
        lang="en"
    )
    assert isinstance(quiz, list)

def test_executor_csv_url_invalid():
    with pytest.raises(ValueError) as exc_info:
        executor(
            file_url="https://filesamples.com/samples/document/csv/sample1.csv",
            file_type=1,
            lang="en"
        )
    assert isinstance(exc_info.value, ValueError)

# TXT Tests
def test_executor_txt_url_valid():
    quiz = executor(
        file_url="https://filesamples.com/samples/document/txt/sample1.txt",
        file_type="txt",
        lang="en"
    )
    assert isinstance(quiz, list)

def test_executor_txt_url_invalid():
    with pytest.raises(ValueError) as exc_info:
        executor(
            file_url="https://filesamples.com/samples/document/txt/sample1.txt",
            file_type=1,
            lang="en"
        )
    assert isinstance(exc_info.value, ValueError)

# MD Tests
def test_executor_md_url_valid():
    quiz = executor(
        file_url="https://github.com/radicalxdev/kai-ai-backend/blob/main/README.md",
        file_type="md",
        lang="en"
    )
    assert isinstance(quiz, list)

def test_executor_md_url_invalid():
    with pytest.raises(ValueError) as exc_info:
        executor(
            file_url="https://github.com/radicalxdev/kai-ai-backend/blob/main/README.md",
            file_type=1,
            lang="en"
        )
    assert isinstance(exc_info.value, ValueError)

# PPTX Tests
def test_executor_pptx_url_valid():
    quiz = executor(
        file_url="https://scholar.harvard.edu/files/torman_personal/files/samplepptx.pptx",
        file_type="pptx",
        lang="en"
    )
    assert isinstance(quiz, list)

def test_executor_pptx_url_invalid():
    with pytest.raises(ValueError) as exc_info:
        executor(
            file_url="https://scholar.harvard.edu/files/torman_personal/files/samplepptx.pptx",
            file_type=1,
            lang="en"
        )
    assert isinstance(exc_info.value, ValueError)

# DOCX Tests
def test_executor_docx_url_valid():
    quiz = executor(
        file_url="https://filesamples.com/samples/document/docx/sample1.docx",
        file_type="docx",
        lang="en"
    )
    assert isinstance(quiz, list)

def test_executor_docx_url_invalid():
    with pytest.raises(ValueError) as exc_info:
        executor(
            file_url="https://filesamples.com/samples/document/docx/sample1.docx",
            file_type=1,
            lang="en"
        )
    assert isinstance(exc_info.value, ValueError)

# XLS Tests
def test_executor_xls_url_valid():
    quiz = executor(
        file_url="https://filesamples.com/samples/document/xls/sample1.xls",
        file_type="xls",
        lang="en"
    )
    assert isinstance(quiz, list)

def test_executor_xls_url_invalid():
    with pytest.raises(ValueError) as exc_info:
        executor(
            file_url="https://filesamples.com/samples/document/xls/sample1.xls",
            file_type=1,
            lang="en"
        )
    assert isinstance(exc_info.value, ValueError)

# XLSX Tests
def test_executor_xlsx_url_valid():
    quiz = executor(
        file_url="https://filesamples.com/samples/document/xlsx/sample1.xlsx",
        file_type="xlsx",
        lang="en"
    )
    assert isinstance(quiz, list)

def test_executor_xlsx_url_invalid():
    with pytest.raises(ValueError) as exc_info:
        executor(
            file_url="https://filesamples.com/samples/document/xlsx/sample1.xlsx",
            file_type=1,
            lang="en"
        )
    assert isinstance(exc_info.value, ValueError)

# XML Tests
def test_executor_xml_url_invalid():
    with pytest.raises(ValueError) as exc_info:
        executor(
            file_url="https://filesampleshub.com/download/code/xml/dummy.xml",
            file_type=1,
            lang="en"
        )
    assert isinstance(exc_info.value, ValueError)

# Google Docs Tests
def test_executor_gdocs_url_invalid():
    with pytest.raises(ValueError) as exc_info:
        executor(
            file_url="https://docs.google.com/document/d/1OWQfO9LX6psGipJu9LabzNE22us1Ct/edit",
            file_type=1,
            lang="en"
        )
    assert isinstance(exc_info.value, ValueError)

# Google Sheets Tests
def test_executor_gsheets_url_invalid():
    with pytest.raises(ValueError) as exc_info:
        executor(
            file_url="https://docs.google.com/spreadsheets/d/16OPtLLSfU/edit",
            file_type=1,
            lang="en"
        )
    assert isinstance(exc_info.value, ValueError)

# Google Slides Tests
def test_executor_gslides_url_invalid():
    with pytest.raises(ValueError) as exc_info:
        executor(
            file_url="https://docs.google.com/spreadsheets/d/16OPtLLSfU/edit",
            file_type=1,
            lang="en"
        )
    assert isinstance(exc_info.value, ValueError)

# Google PDFs Tests
def test_executor_gpdfs_url_valid():
    quiz = executor(
        file_url="https://drive.google.com/file/d/1fUj1uWIMh6QZsPkt0Vs7mEd2VEqz3O8l/view",
        file_type="gpdf",
        lang="en"
    )
    assert isinstance(quiz, list)

def test_executor_gpdfs_url_invalid():
    with pytest.raises(ValueError) as exc_info:
        executor(
            file_url="https://drive.google.com/file/d/1fUj1uWIMh6QZsPkt0Vs7mEd2VEqz3O8l/view",
            file_type=1,
            lang="en"
        )
    assert isinstance(exc_info.value, ValueError)

# MP3 Tests
def test_executor_mp3_url_invalid():
    with pytest.raises(ValueError) as exc_info:
        executor(
            file_url="https://raw.githubusercontent.com/asleem/uploaded_files/main/dummy.mp3",
            file_type=1,
            lang="en"
        )
    assert isinstance(exc_info.value, ValueError)