import pytest
from app.tools.ai_resistant_assignments_generator.core import executor

# Base attributes reused across all tests
base_attributes = {
    "grade_level": "university",
    "assignment_description": "Math Homework",
    "lang": "en"
}

# Parametrized test cases
@pytest.mark.parametrize(
    "file_url, file_type, should_raise, expected",
    [
        # PDF Tests
        ("https://filesamples.com/samples/document/pdf/sample1.pdf", "pdf", False, dict),
        ("https://filesamples.com/samples/document/pdf/sample1.pdf", 1, True, ValueError),
        
        # CSV Tests
        ("https://filesamples.com/samples/document/csv/sample1.csv", "csv", False, dict),
        ("https://filesamples.com/samples/document/csv/sample1.csv", 1, True, ValueError),
        
        # TXT Tests
        ("https://filesamples.com/samples/document/txt/sample1.txt", "txt", False, dict),
        ("https://filesamples.com/samples/document/txt/sample1.txt", 1, True, ValueError),
        
        # MD Tests
        ("https://github.com/radicalxdev/kai-ai-backend/blob/main/README.md", "md", False, dict),
        ("https://github.com/radicalxdev/kai-ai-backend/blob/main/README.md", 1, True, ValueError),
        
        # PPTX Tests
        ("https://scholar.harvard.edu/files/torman_personal/files/samplepptx.pptx", "pptx", False, dict),
        ("https://scholar.harvard.edu/files/torman_personal/files/samplepptx.pptx", 1, True, ValueError),
        
        # DOCX Tests
        ("https://filesamples.com/samples/document/docx/sample1.docx", "docx", False, dict),
        ("https://filesamples.com/samples/document/docx/sample1.docx", 1, True, ValueError),
        
        # XLS Tests
        ("https://filesamples.com/samples/document/xls/sample1.xls", "xls", False, dict),
        ("https://filesamples.com/samples/document/xls/sample1.xls", 1, True, ValueError),
        
        # XLSX Tests
        ("https://filesamples.com/samples/document/xlsx/sample1.xlsx", "xlsx", False, dict),
        ("https://filesamples.com/samples/document/xlsx/sample1.xlsx", 1, True, ValueError),
        
        # GPDF Tests
        ("https://drive.google.com/file/d/1fUj1uWIMh6QZsPkt0Vs7mEd2VEqz3O8l/view", "gpdf", False, dict),
        ("https://drive.google.com/file/d/1fUj1uWIMh6QZsPkt0Vs7mEd2VEqz3O8l/view", 1, True, ValueError),
        
        # Invalid Tests
        ("https://filesampleshub.com/download/code/xml/dummy.xml", 1, True, ValueError),
        ("https://docs.google.com/document/d/1OWQfO9LX6psGipJu9LabzNE22us1Ct/edit", 1, True, ValueError),
        ("https://docs.google.com/spreadsheets/d/16OPtLLSfU/edit", 1, True, ValueError),
        ("https://raw.githubusercontent.com/asleem/uploaded_files/main/dummy.mp3", 1, True, ValueError),
    ],
)
def test_executor(file_url, file_type, should_raise, expected):
    if should_raise:
        with pytest.raises(expected):
            executor(
                **base_attributes,
                file_url=file_url,
                file_type=file_type
            )
    else:
        result = executor(
            **base_attributes,
            file_url=file_url,
            file_type=file_type
        )
        assert isinstance(result, expected)
