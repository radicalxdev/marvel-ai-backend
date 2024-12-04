import pytest
from app.features.lesson_plan_generator.core import executor
from app.features.lesson_plan_generator.tools import LessonPlan

# Base attributes reused across all tests
base_attributes = {
    "grade_level": "university",
    "topic": "Linear Algebra",
    "objectives": "",
    "additional_customization": "",
    "ac_file_url": "https://docs.google.com/document/d/1IsTPJSgWMdD20tXMm1sXJSCc0xz9Kxmn/edit?usp=sharing&ouid=107052763106493355624&rtpof=true&sd=true",
    "ac_file_type": "gdoc",
    "lang": "en"
}

# PDF Tests
def test_executor_pdf_objectives_url_valid():
    lesson_plan = executor(
        **base_attributes,
        objectives_file_url="https://filesamples.com/samples/document/pdf/sample1.pdf",
        objectives_file_type="pdf"
    )
    assert isinstance(lesson_plan, dict)

def test_executor_pdf_objectives_url_invalid():
    with pytest.raises(ValueError) as exc_info:
        executor(
            **base_attributes,
            objectives_file_url="https://filesamples.com/samples/document/pdf/sample1.pdf",
            objectives_file_type=1
        )
    assert isinstance(exc_info.value, ValueError)
    
# CSV Tests
def test_executor_csv_objectives_url_valid():
    lesson_plan = executor(
        **base_attributes,
        objectives_file_url="https://filesamples.com/samples/document/csv/sample1.csv",
        objectives_file_type="csv"
    )
    assert isinstance(lesson_plan, dict)

def test_executor_csv_objectives_url_invalid():
    with pytest.raises(ValueError) as exc_info:
        executor(
            **base_attributes,
            objectives_file_url="https://filesamples.com/samples/document/csv/sample1.csv",
            objectives_file_type=1
        )
    assert isinstance(exc_info.value, ValueError)

# TXT Tests
def test_executor_txt_objectives_url_valid():
    lesson_plan = executor(
        **base_attributes,
        objectives_file_url="https://filesamples.com/samples/document/txt/sample1.txt",
        objectives_file_type="txt"
    )
    assert isinstance(lesson_plan, dict)

def test_executor_txt_objectives_url_invalid():
    with pytest.raises(ValueError) as exc_info:
        executor(
            **base_attributes,
            objectives_file_url="https://filesamples.com/samples/document/txt/sample1.txt",
            objectives_file_type=1
        )
    assert isinstance(exc_info.value, ValueError)

# MD Tests
def test_executor_md_objectives_url_valid():
    lesson_plan = executor(
        **base_attributes,
        objectives_file_url="https://github.com/radicalxdev/kai-ai-backend/blob/main/README.md",
        objectives_file_type="md"
    )
    assert isinstance(lesson_plan, dict)

def test_executor_md_objectives_url_invalid():
    with pytest.raises(ValueError) as exc_info:
        executor(
            **base_attributes,
            objectives_file_url="https://github.com/radicalxdev/kai-ai-backend/blob/main/README.md",
            objectives_file_type=1
        )
    assert isinstance(exc_info.value, ValueError)

# PPTX Tests
def test_executor_pptx_objectives_url_valid():
    lesson_plan = executor(
        **base_attributes,
        objectives_file_url="https://scholar.harvard.edu/files/torman_personal/files/samplepptx.pptx",
        objectives_file_type="pptx"
    )
    assert isinstance(lesson_plan, dict)

def test_executor_pptx_objectives_url_invalid():
    with pytest.raises(ValueError) as exc_info:
        executor(
            **base_attributes,
            objectives_file_url="https://scholar.harvard.edu/files/torman_personal/files/samplepptx.pptx",
            objectives_file_type=1
        )
    assert isinstance(exc_info.value, ValueError)

# DOCX Tests
def test_executor_docx_objectives_url_valid():
    lesson_plan = executor(
        **base_attributes,
        objectives_file_url="https://filesamples.com/samples/document/docx/sample1.docx",
        objectives_file_type="docx"
    )
    assert isinstance(lesson_plan, dict)

def test_executor_docx_objectives_url_invalid():
    with pytest.raises(ValueError) as exc_info:
        executor(
            **base_attributes,
            objectives_file_url="https://filesamples.com/samples/document/docx/sample1.docx",
            objectives_file_type=1
        )
    assert isinstance(exc_info.value, ValueError)

# XLS Tests
def test_executor_xls_objectives_url_valid():
    lesson_plan = executor(
        **base_attributes,
        objectives_file_url="https://filesamples.com/samples/document/xls/sample1.xls",
        objectives_file_type="xls"
    )
    assert isinstance(lesson_plan, dict)

def test_executor_xls_objectives_url_invalid():
    with pytest.raises(ValueError) as exc_info:
        executor(
            **base_attributes,
            objectives_file_url="https://filesamples.com/samples/document/xls/sample1.xls",
            objectives_file_type=1
        )
    assert isinstance(exc_info.value, ValueError)

# XLSX Tests
def test_executor_xlsx_objectives_url_valid():
    lesson_plan = executor(
        **base_attributes,
        objectives_file_url="https://filesamples.com/samples/document/xlsx/sample1.xlsx",
        objectives_file_type="xlsx"
    )
    assert isinstance(lesson_plan, dict)

def test_executor_xlsx_objectives_url_invalid():
    with pytest.raises(ValueError) as exc_info:
        executor(
            **base_attributes,
            objectives_file_url="https://filesamples.com/samples/document/xlsx/sample1.xlsx",
            objectives_file_type=1
        )
    assert isinstance(exc_info.value, ValueError)

# GPDF Tests
def test_executor_gpdf_objectives_url_valid():
    lesson_plan = executor(
        **base_attributes,
        objectives_file_url="https://drive.google.com/file/d/1fUj1uWIMh6QZsPkt0Vs7mEd2VEqz3O8l/view",
        objectives_file_type="gpdf"
    )
    assert isinstance(lesson_plan, dict)

def test_executor_gpdf_objectives_url_invalid():
    with pytest.raises(ValueError) as exc_info:
        executor(
            **base_attributes,
            objectives_file_url="https://drive.google.com/file/d/1fUj1uWIMh6QZsPkt0Vs7mEd2VEqz3O8l/view",
            objectives_file_type=1
        )
    assert isinstance(exc_info.value, ValueError)

# MP3 Tests
def test_executor_mp3_objectives_url_invalid():
    with pytest.raises(ValueError) as exc_info:
        executor(
            **base_attributes,
            objectives_file_url="https://raw.githubusercontent.com/asleem/uploaded_files/main/dummy.mp3",
            objectives_file_type=1
        )
    assert isinstance(exc_info.value, ValueError)
