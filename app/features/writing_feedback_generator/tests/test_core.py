import pytest
from app.features.writing_feedback_generator.core import executor
from app.features.writing_feedback_generator.tools import WritingFeedback

# Base attributes reused across all tests
base_attributes = {
    "grade_level": "university",
    "assignment_description": "Review and provide feedback on the assigned text.",
    "criteria": "",
    "writing_to_review": "",
    "criteria_file_url": "https://docs.google.com/document/d/1IsTPJSgWMdD20tXMm1sXJSCc0xz9Kxmn/edit?usp=sharing&ouid=107052763106493355624&rtpof=true&sd=true",
    "criteria_file_type": "gdoc",
    "lang": "en"
}

# PDF Tests
def test_executor_pdf_wtr_url_valid():
    writing_feedback = executor(
        **base_attributes,
        wtr_file_url="https://filesamples.com/samples/document/pdf/sample1.pdf",
        wtr_file_type="pdf"
    )
    assert isinstance(writing_feedback, WritingFeedback)

def test_executor_pdf_wtr_url_invalid():
    with pytest.raises(ValueError) as exc_info:
        executor(
            **base_attributes,
            wtr_file_url="https://filesamples.com/samples/document/pdf/sample1.pdf",
            wtr_file_type=1
        )
    assert isinstance(exc_info.value, ValueError)

# CSV Tests
def test_executor_csv_wtr_url_valid():
    writing_feedback = executor(
        **base_attributes,
        wtr_file_url="https://filesamples.com/samples/document/csv/sample1.csv",
        wtr_file_type="csv"
    )
    assert isinstance(writing_feedback, WritingFeedback)

def test_executor_csv_wtr_url_invalid():
    with pytest.raises(ValueError) as exc_info:
        executor(
            **base_attributes,
            wtr_file_url="https://filesamples.com/samples/document/csv/sample1.csv",
            wtr_file_type=1
        )
    assert isinstance(exc_info.value, ValueError)

# TXT Tests
def test_executor_txt_wtr_url_valid():
    writing_feedback = executor(
        **base_attributes,
        wtr_file_url="https://filesamples.com/samples/document/txt/sample1.txt",
        wtr_file_type="txt"
    )
    assert isinstance(writing_feedback, WritingFeedback)

def test_executor_txt_wtr_url_invalid():
    with pytest.raises(ValueError) as exc_info:
        executor(
            **base_attributes,
            wtr_file_url="https://filesamples.com/samples/document/txt/sample1.txt",
            wtr_file_type=1
        )
    assert isinstance(exc_info.value, ValueError)

# MD Tests
def test_executor_md_wtr_url_valid():
    writing_feedback = executor(
        **base_attributes,
        wtr_file_url="https://github.com/radicalxdev/kai-ai-backend/blob/main/README.md",
        wtr_file_type="md"
    )
    assert isinstance(writing_feedback, WritingFeedback)

def test_executor_md_wtr_url_invalid():
    with pytest.raises(ValueError) as exc_info:
        executor(
            **base_attributes,
            wtr_file_url="https://github.com/radicalxdev/kai-ai-backend/blob/main/README.md",
            wtr_file_type=1
        )
    assert isinstance(exc_info.value, ValueError)

# PPTX Tests
def test_executor_pptx_wtr_url_valid():
    writing_feedback = executor(
        **base_attributes,
        wtr_file_url="https://scholar.harvard.edu/files/torman_personal/files/samplepptx.pptx",
        wtr_file_type="pptx"
    )
    assert isinstance(writing_feedback, WritingFeedback)

def test_executor_pptx_wtr_url_invalid():
    with pytest.raises(ValueError) as exc_info:
        executor(
            **base_attributes,
            wtr_file_url="https://scholar.harvard.edu/files/torman_personal/files/samplepptx.pptx",
            wtr_file_type=1
        )
    assert isinstance(exc_info.value, ValueError)

# DOCX Tests
def test_executor_docx_wtr_url_valid():
    writing_feedback = executor(
        **base_attributes,
        wtr_file_url="https://filesamples.com/samples/document/docx/sample1.docx",
        wtr_file_type="docx"
    )
    assert isinstance(writing_feedback, WritingFeedback)

def test_executor_docx_wtr_url_invalid():
    with pytest.raises(ValueError) as exc_info:
        executor(
            **base_attributes,
            wtr_file_url="https://filesamples.com/samples/document/docx/sample1.docx",
            wtr_file_type=1
        )
    assert isinstance(exc_info.value, ValueError)

# XLS Tests
def test_executor_xls_wtr_url_valid():
    writing_feedback = executor(
        **base_attributes,
        wtr_file_url="https://filesamples.com/samples/document/xls/sample1.xls",
        wtr_file_type="xls"
    )
    assert isinstance(writing_feedback, WritingFeedback)

def test_executor_xls_wtr_url_invalid():
    with pytest.raises(ValueError) as exc_info:
        executor(
            **base_attributes,
            wtr_file_url="https://filesamples.com/samples/document/xls/sample1.xls",
            wtr_file_type=1
        )
    assert isinstance(exc_info.value, ValueError)

# XLSX Tests
def test_executor_xlsx_wtr_url_valid():
    writing_feedback = executor(
        **base_attributes,
        wtr_file_url="https://filesamples.com/samples/document/xlsx/sample1.xlsx",
        wtr_file_type="xlsx"
    )
    assert isinstance(writing_feedback, WritingFeedback)

def test_executor_xlsx_wtr_url_invalid():
    with pytest.raises(ValueError) as exc_info:
        executor(
            **base_attributes,
            wtr_file_url="https://filesamples.com/samples/document/xlsx/sample1.xlsx",
            wtr_file_type=1
        )
    assert isinstance(exc_info.value, ValueError)

# GPDF Tests
def test_executor_gpdf_wtr_url_valid():
    writing_feedback = executor(
        **base_attributes,
        wtr_file_url="https://drive.google.com/file/d/1fUj1uWIMh6QZsPkt0Vs7mEd2VEqz3O8l/view",
        wtr_file_type="gpdf"
    )
    assert isinstance(writing_feedback, WritingFeedback)

def test_executor_gpdf_wtr_url_invalid():
    with pytest.raises(ValueError) as exc_info:
        executor(
            **base_attributes,
            wtr_file_url="https://drive.google.com/file/d/1fUj1uWIMh6QZsPkt0Vs7mEd2VEqz3O8l/view",
            wtr_file_type=1
        )
    assert isinstance(exc_info.value, ValueError)

# MP3 Tests
def test_executor_mp3_wtr_url_invalid():
    with pytest.raises(ValueError) as exc_info:
        executor(
            **base_attributes,
            wtr_file_url="https://raw.githubusercontent.com/asleem/uploaded_files/main/dummy.mp3",
            wtr_file_type=1
        )
    assert isinstance(exc_info.value, ValueError)
