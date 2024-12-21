import pytest
from app.tools.connect_with_them.core import executor

# Base attributes reused across all tests
base_attributes = {
    "grade_level": "5th grade",
    "task_description": "",
    "students_description": "",
    "sd_file_url": "https://docs.google.com/document/d/1IsTPJSgWMdD20tXMm1sXJSCc0xz9Kxmn/edit?usp=sharing&ouid=107052763106493355624&rtpof=true&sd=true",
    "sd_file_type": "gdoc",
    "lang": "en"
}

# PDF Tests
def test_executor_pdf_td_url_valid():
    connect_with_them = executor(
        **base_attributes,
        td_file_url="https://filesamples.com/samples/document/pdf/sample1.pdf",
        td_file_type="pdf"
    )
    assert isinstance(connect_with_them, dict)

def test_executor_pdf_td_url_invalid():
    with pytest.raises(ValueError) as exc_info:
        executor(
            **base_attributes,
            td_file_url="https://filesamples.com/samples/document/pdf/sample1.pdf",
            td_file_type=1
        )
    assert isinstance(exc_info.value, ValueError)

# CSV Tests
def test_executor_csv_td_url_valid():
    connect_with_them = executor(
        **base_attributes,
        td_file_url="https://filesamples.com/samples/document/csv/sample1.csv",
        td_file_type="csv"
    )
    assert isinstance(connect_with_them, dict)

def test_executor_csv_td_url_invalid():
    with pytest.raises(ValueError) as exc_info:
        executor(
            **base_attributes,
            td_file_url="https://filesamples.com/samples/document/csv/sample1.csv",
            td_file_type=1
        )
    assert isinstance(exc_info.value, ValueError)

# TXT Tests
def test_executor_txt_td_url_valid():
    connect_with_them = executor(
        **base_attributes,
        td_file_url="https://filesamples.com/samples/document/txt/sample1.txt",
        td_file_type="txt"
    )
    assert isinstance(connect_with_them, dict)

def test_executor_txt_td_url_invalid():
    with pytest.raises(ValueError) as exc_info:
        executor(
            **base_attributes,
            td_file_url="https://filesamples.com/samples/document/txt/sample1.txt",
            td_file_type=1
        )
    assert isinstance(exc_info.value, ValueError)

# MD Tests
def test_executor_md_td_url_valid():
    connect_with_them = executor(
        **base_attributes,
        td_file_url="https://github.com/radicalxdev/kai-ai-backend/blob/main/README.md",
        td_file_type="md"
    )
    assert isinstance(connect_with_them, dict)

def test_executor_md_td_url_invalid():
    with pytest.raises(ValueError) as exc_info:
        executor(
            **base_attributes,
            td_file_url="https://github.com/radicalxdev/kai-ai-backend/blob/main/README.md",
            td_file_type=1
        )
    assert isinstance(exc_info.value, ValueError)

# PPTX Tests
def test_executor_pptx_td_url_valid():
    connect_with_them = executor(
        **base_attributes,
        td_file_url="https://scholar.harvard.edu/files/torman_personal/files/samplepptx.pptx",
        td_file_type="pptx"
    )
    assert isinstance(connect_with_them, dict)

def test_executor_pptx_td_url_invalid():
    with pytest.raises(ValueError) as exc_info:
        executor(
            **base_attributes,
            td_file_url="https://scholar.harvard.edu/files/torman_personal/files/samplepptx.pptx",
            td_file_type=1
        )
    assert isinstance(exc_info.value, ValueError)

# DOCX Tests
def test_executor_docx_td_url_valid():
    connect_with_them = executor(
        **base_attributes,
        td_file_url="https://filesamples.com/samples/document/docx/sample1.docx",
        td_file_type="docx"
    )
    assert isinstance(connect_with_them, dict)

def test_executor_docx_td_url_invalid():
    with pytest.raises(ValueError) as exc_info:
        executor(
            **base_attributes,
            td_file_url="https://filesamples.com/samples/document/docx/sample1.docx",
            td_file_type=1
        )
    assert isinstance(exc_info.value, ValueError)

# XLS Tests
def test_executor_xls_td_url_valid():
    connect_with_them = executor(
        **base_attributes,
        td_file_url="https://filesamples.com/samples/document/xls/sample1.xls",
        td_file_type="xls"
    )
    assert isinstance(connect_with_them, dict)

def test_executor_xls_td_url_invalid():
    with pytest.raises(ValueError) as exc_info:
        executor(
            **base_attributes,
            td_file_url="https://filesamples.com/samples/document/xls/sample1.xls",
            td_file_type=1
        )
    assert isinstance(exc_info.value, ValueError)

# XLSX Tests
def test_executor_xlsx_td_url_valid():
    connect_with_them = executor(
        **base_attributes,
        td_file_url="https://filesamples.com/samples/document/xlsx/sample1.xlsx",
        td_file_type="xlsx"
    )
    assert isinstance(connect_with_them, dict)

def test_executor_xlsx_td_url_invalid():
    with pytest.raises(ValueError) as exc_info:
        executor(
            **base_attributes,
            td_file_url="https://filesamples.com/samples/document/xlsx/sample1.xlsx",
            td_file_type=1
        )
    assert isinstance(exc_info.value, ValueError)

# GPDF Tests
def test_executor_gpdf_td_url_valid():
    connect_with_them = executor(
        **base_attributes,
        td_file_url="https://drive.google.com/file/d/1fUj1uWIMh6QZsPkt0Vs7mEd2VEqz3O8l/view",
        td_file_type="gpdf"
    )
    assert isinstance(connect_with_them, dict)

def test_executor_gpdf_td_url_invalid():
    with pytest.raises(ValueError) as exc_info:
        executor(
            **base_attributes,
            td_file_url="https://drive.google.com/file/d/1fUj1uWIMh6QZsPkt0Vs7mEd2VEqz3O8l/view",
            td_file_type=1
        )
    assert isinstance(exc_info.value, ValueError)

# MP3 Tests
def test_executor_mp3_td_url_invalid():
    with pytest.raises(ValueError) as exc_info:
        executor(
            **base_attributes,
            td_file_url="https://raw.githubusercontent.com/asleem/uploaded_files/main/dummy.mp3",
            td_file_type=1
        )
    assert isinstance(exc_info.value, ValueError)
