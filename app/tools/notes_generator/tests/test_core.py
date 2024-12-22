import os
import pytest
from app.tools.notes_generator.core import executor

# Base attributes reused across all tests
base_attributes = {
        "topic" : "Topic of the provided documents",
        "nb_columns" : 1,
        "details" : "information about the topic",
        "orientation" : "portrait",
        "lang" : "en"
    }

# PDF Tests
def test_executor_pdf_url_valid():
    notes = executor(
        **base_attributes,
        file_urls="https://filesamples.com/samples/document/pdf/sample1.pdf",
        file_types="pdf"
    )
    assert isinstance(notes, dict)

def test_executor_pdf_url_invalid():
    with pytest.raises(ValueError) as exc_info:
        executor(
            **base_attributes,
            file_urls="https://filesamples.com/samples/document/pdf/sample1.pdf",
            file_types=1
        )
    assert isinstance(exc_info.value, ValueError)

# CSV Tests
def test_executor_csv_url_valid():
    notes = executor(
        **base_attributes,
        file_urls="https://filesamples.com/samples/document/csv/sample1.csv",
        file_types="csv"
    )
    assert isinstance(notes, dict)

def test_executor_csv_url_invalid():
    with pytest.raises(ValueError) as exc_info:
        executor(
            **base_attributes,
            file_urls="https://filesamples.com/samples/document/csv/sample1.csv",
            file_types=1
        )
    assert isinstance(exc_info.value, ValueError)

# TXT Tests
def test_executor_txt_url_valid():
    notes = executor(
        **base_attributes,
        file_urls="https://filesamples.com/samples/document/txt/sample1.txt",
        file_types="txt"
    )
    assert isinstance(notes, dict)

def test_executor_txt_url_invalid():
    with pytest.raises(ValueError) as exc_info:
        executor(
            **base_attributes,
            file_urls="https://filesamples.com/samples/document/txt/sample1.txt",
            file_types=1
        )
    assert isinstance(exc_info.value, ValueError)

# MD Tests
def test_executor_md_url_valid():
    notes = executor(
        **base_attributes,
        file_urls="https://github.com/radicalxdev/kai-ai-backend/blob/main/README.md",
        file_types="md"
    )
    assert isinstance(notes, dict)

def test_executor_md_url_invalid():
    with pytest.raises(ValueError) as exc_info:
        executor(
            **base_attributes,
            file_urls="https://github.com/radicalxdev/kai-ai-backend/blob/main/README.md",
            file_types=1
        )
    assert isinstance(exc_info.value, ValueError)

# PPTX Tests
def test_executor_pptx_url_valid():
    notes = executor(
        **base_attributes,
        file_urls="https://scholar.harvard.edu/files/torman_personal/files/samplepptx.pptx",
        file_types="pptx"
    )
    assert isinstance(notes, dict)

def test_executor_pptx_url_invalid():
    with pytest.raises(ValueError) as exc_info:
        executor(
            **base_attributes,
            file_urls="https://scholar.harvard.edu/files/torman_personal/files/samplepptx.pptx",
            file_types=1
        )
    assert isinstance(exc_info.value, ValueError)

# DOCX Tests
def test_executor_docx_url_valid():
    notes = executor(
        **base_attributes,
        file_urls="https://filesamples.com/samples/document/docx/sample1.docx",
        file_types="docx"
    )
    assert isinstance(notes, dict)

def test_executor_docx_url_invalid():
    with pytest.raises(ValueError) as exc_info:
        executor(
            **base_attributes,
            file_urls="https://filesamples.com/samples/document/docx/sample1.docx",
            file_types=1
        )
    assert isinstance(exc_info.value, ValueError)

# XLS Tests
def test_executor_xls_url_valid():
    notes = executor(
        **base_attributes,
        file_urls="https://filesamples.com/samples/document/xls/sample1.xls",
        file_types="xls"
    )
    assert isinstance(notes, dict)

def test_executor_xls_url_invalid():
    with pytest.raises(ValueError) as exc_info:
        executor(
            **base_attributes,
            file_urls="https://filesamples.com/samples/document/xls/sample1.xls",
            file_types=1
        )
    assert isinstance(exc_info.value, ValueError)

# XLSX Tests
def test_executor_xlsx_url_valid():
    notes = executor(
        **base_attributes,
        file_urls="https://filesamples.com/samples/document/xlsx/sample1.xlsx",
        file_types="xlsx"
    )
    assert isinstance(notes, dict)

def test_executor_xlsx_url_invalid():
    with pytest.raises(ValueError) as exc_info:
        executor(
            **base_attributes,
            file_urls="https://filesamples.com/samples/document/xlsx/sample1.xlsx",
            file_types=1
        )
    assert isinstance(exc_info.value, ValueError)

# XML Tests
def test_executor_xml_url_invalid():
    with pytest.raises(ValueError) as exc_info:
        executor(
            **base_attributes,
            file_urls="https://filesampleshub.com/download/code/xml/dummy.xml",
            file_types=1
        )
    assert isinstance(exc_info.value, ValueError)

# GDocs Tests
def test_executor_gdocs_url_invalid():
    with pytest.raises(ValueError) as exc_info:
        executor(
            **base_attributes,
            file_urls="https://docs.google.com/document/d/1OWQfO9LX6psGipJu9LabzNE22us1Ct/edit",
            file_types=1
        )
    assert isinstance(exc_info.value, ValueError)

# GSheets Tests
def test_executor_gsheets_url_invalid():
    with pytest.raises(ValueError) as exc_info:
        executor(
            **base_attributes,
            file_urls="https://docs.google.com/spreadsheets/d/16OPtLLSfU/edit",
            file_types=1
        )
    assert isinstance(exc_info.value, ValueError)

# GSlides Tests
def test_executor_gslides_url_invalid():
    with pytest.raises(ValueError) as exc_info:
        executor(
            **base_attributes,
            file_urls="https://docs.google.com/spreadsheets/d/16OPtLLSfU/edit",
            file_types=1
        )
    assert isinstance(exc_info.value, ValueError)

# GPDFs Tests
def test_executor_gpdfs_url_valid():
    notes = executor(
        **base_attributes,
        file_urls="https://drive.google.com/file/d/1fUj1uWIMh6QZsPkt0Vs7mEd2VEqz3O8l/view",
        file_types="gpdf"
    )
    assert isinstance(notes, dict)

def test_executor_gpdfs_url_invalid():
    with pytest.raises(ValueError) as exc_info:
        executor(
            **base_attributes,
            file_urls="https://drive.google.com/file/d/1fUj1uWIMh6QZsPkt0Vs7mEd2VEqz3O8l/view",
            file_types=1
        )
    assert isinstance(exc_info.value, ValueError)

# MP3 Tests
def test_executor_mp3_url_invalid():
    with pytest.raises(ValueError) as exc_info:
        executor(
            **base_attributes,
            file_urls="https://raw.githubusercontent.com/asleem/uploaded_files/main/dummy.mp3",
            file_types=1
        )
    assert isinstance(exc_info.value, ValueError)

