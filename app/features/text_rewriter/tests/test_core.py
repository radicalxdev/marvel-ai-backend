import pytest
from app.features.text_rewriter.core import executor

base_attributes = {
    "instructions": "Summarize the text for a middle school audience.",
    "lang": "",
    "verbose":True
}

# Plain Text Tests
def test_executor_plain_text_valid():
    output = executor(
        **base_attributes,
        text="Romeo and Juliet is a tragic play by William Shakespeare that tells the story of two young lovers whose deaths ultimately reconcile their feuding families.",
        file_url = "",
        file_type = ""
    )
    assert isinstance(output, dict)

def test_executor_plain_text_invalid():
    with pytest.raises(ValueError) as exc_info:
        executor(
        **base_attributes,
        text = "Romeo and Juliet is a tragic play by William Shakespeare that tells the story of two young lovers whose deaths ultimately reconcile their feuding families.",
        file_url = "",
        file_type = 1
    )
    assert isinstance(exc_info.value, ValueError)

# PDF Tests
def test_executor_pdf_url_valid():
    output = executor(
        **base_attributes,
        text = "",
        file_url = "https://firebasestorage.googleapis.com/v0/b/kai-ai-f63c8.appspot.com/o/uploads%2F510f946e-823f-42d7-b95d-d16925293946-Linear%20Regression%20Stat%20Yale.pdf?alt=media&token=caea86aa-c06b-4cde-9fd0-42962eb72ddd",
        file_type = "pdf"
    )
    assert isinstance(output, dict)

def test_executor_pdf_url_invalid():
    with pytest.raises(ValueError) as exc_info:
        executor(
        **base_attributes,
        text = "",
        file_url = "https://firebasestorage.googleapis.com/v0/b/kai-ai-f63c8.appspot.com/o/uploads%2F510f946e-823f-42d7-b95d-d16925293946-Linear%20Regression%20Stat%20Yale.pdf?alt=media&token=caea86aa-c06b-4cde-9fd0-42962eb72ddd",
        file_type = 1
    )
    assert isinstance(exc_info.value, ValueError)


# DOCX Tests
def test_executor_docx_valid():
    output = executor(
        **base_attributes,
        text="",
        file_url="https://filesamples.com/samples/document/docx/sample1.docx",
        file_type="docx"
    )
    assert isinstance(output, dict)

def test_executor_docx_invalid():
    with pytest.raises(ValueError) as exc_info:
        executor(
            **base_attributes,
            text="",
            file_url="https://filesamples.com/samples/document/docx/sample1.docx",
            file_type=1
        )
    assert isinstance(exc_info.value, ValueError)

# # PPT Tests
def test_executor_ppt_valid():
    output = executor(
        **base_attributes,
        text="",
        file_url="https://scholar.harvard.edu/files/torman_personal/files/samplepptx.pptx",
        file_type="pptx"
    )
    assert isinstance(output, dict)

def test_executor_ppt_invalid():
    with pytest.raises(ValueError) as exc_info:
        executor(
            **base_attributes,
            text="",
            file_url="https://scholar.harvard.edu/files/torman_personal/files/samplepptx.pptx",
            file_type=1
        )
    assert isinstance(exc_info.value, ValueError)

# Youtube Video URL Tests
def test_executor_youtube_valid():
    output = executor(
        **base_attributes,
        text="",
        file_url="https://www.youtube.com/watch?v=HgBpFaATdoA",
        file_type="youtube_url"
    )
    assert isinstance(output, dict)

def test_executor_youtube_invalid():
    with pytest.raises(ValueError) as exc_info:
        executor(
            **base_attributes,
            text="",
            file_url="https://www.youtube.com/watch?v=HgBpFaATdoA",
            file_type=1
        )
    assert isinstance(exc_info.value, ValueError)


# GDOCS Tests
def test_executor_gdocs_valid():
    output = executor(
        **base_attributes,
        text="",
        file_url="https://docs.google.com/document/d/1DkOTKlHnZC6Us2N-ZHgECsQezYoB49af/edit?usp=drive_link&ouid=107052763106493355624&rtpof=true&sd=true",
        file_type="gdoc"
    )
    assert isinstance(output, dict)

def test_executor_gdocs_invalid():
    with pytest.raises(ValueError) as exc_info:
        executor(
            **base_attributes,
            text="",
            file_url="https://docs.google.com/document/d/1DkOTKlHnZC6Us2N-ZHgECsQezYoB49af/edit?usp=drive_link&ouid=107052763106493355624&rtpof=true&sd=true",
            file_type=1
        )
    assert isinstance(exc_info.value, ValueError)

# Google Sheet Tests
def test_executor_gdocs_valid():
    output = executor(
        **base_attributes,
        text="",
        file_url="https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit?gid=0#gid=0",
        file_type="gsheet"
    )
    assert isinstance(output, dict)

def test_executor_gdocs_invalid():
    with pytest.raises(ValueError) as exc_info:
        executor(
            **base_attributes,
            text="",
            file_url="https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit?gid=0#gid=0",
            file_type=1
        )
    assert isinstance(exc_info.value, ValueError)


# XLSX Tests
def test_executor_xlsx_url_valid():
    lesson_plan = executor(
        **base_attributes,
        text="",
        file_url="https://filesamples.com/samples/document/xlsx/sample1.xlsx",
        file_type="xlsx"
    )
    assert isinstance(lesson_plan, dict)

def test_executor_xlsx_url_invalid():
    with pytest.raises(ValueError) as exc_info:
        executor(
            **base_attributes,
            text="",
            file_url="https://filesamples.com/samples/document/xlsx/sample1.xlsx",
            file_type=1
        )
    assert isinstance(exc_info.value, ValueError)


# GPDF Tests
def test_executor_gpdf_url_valid():
    lesson_plan = executor(
        **base_attributes,
        text="",
        file_url="https://drive.google.com/file/d/1fUj1uWIMh6QZsPkt0Vs7mEd2VEqz3O8l/view",
        file_type="gpdf"
    )
    assert isinstance(lesson_plan, dict)

def test_executor_gpd_url_invalid():
    with pytest.raises(ValueError) as exc_info:
        executor(
            **base_attributes,
            text="",
            file_url="https://drive.google.com/file/d/1fUj1uWIMh6QZsPkt0Vs7mEd2VEqz3O8l/view",
            file_type=1
        )
    assert isinstance(exc_info.value, ValueError)


# MD Tests
def test_executor_md_url_valid():
    lesson_plan = executor(
        **base_attributes,
        text="",
        file_url="https://github.com/radicalxdev/kai-ai-backend/blob/main/README.md",
        file_type="md"
    )
    assert isinstance(lesson_plan, dict)

def test_executor_md_url_invalid():
    with pytest.raises(ValueError) as exc_info:
        executor(
            **base_attributes,
            text="",
            file_url="https://github.com/radicalxdev/kai-ai-backend/blob/main/README.md",
            file_type=1
        )
    assert isinstance(exc_info.value, ValueError)



# TXT Tests
def test_executor_txt_url_valid():
    lesson_plan = executor(
        **base_attributes,
        text="",
        file_url="https://filesamples.com/samples/document/txt/sample1.txt",
        file_type="txt"
    )
    assert isinstance(lesson_plan, dict)

def test_executor_txt_url_invalid():
    with pytest.raises(ValueError) as exc_info:
        executor(
            **base_attributes,
            text="",
            file_url="https://filesamples.com/samples/document/txt/sample1.txt",
            file_type=1
        )
    assert isinstance(exc_info.value, ValueError)


# CSV Tests
def test_executor_csv_url_valid():
    lesson_plan = executor(
        **base_attributes,
        text="",
        file_url="https://filesamples.com/samples/document/csv/sample1.csv",
        file_type="csv"
    )
    assert isinstance(lesson_plan, dict)

def test_executor_csv_url_invalid():
    with pytest.raises(ValueError) as exc_info:
        executor(
            **base_attributes,
            text="",
            file_url="https://filesamples.com/samples/document/csv/sample1.csv",
            file_type=1
        )
    assert isinstance(exc_info.value, ValueError)
