import unittest
import pytest
from pytest import MonkeyPatch
from datetime import datetime
from unittest.mock import patch, Mock
from app.api.error_utilities import LoaderError, InputValidationError, ToolExecutorError, ErrorResponse
from app.features.syllabus_generator.tools import SyllabusGenerator, read_text_file
from app.features.syllabus_generator.core import executor

def test_read_text_file(tmp_path):
    file_path = tmp_path / "test.txt"
    with open(file_path, 'w') as file:
        file.write("This is a test file.")
    result = read_text_file(str(file_path))
    assert result == "This is a test file."

@pytest.fixture
def setup_data():
    return {
        "grade_level": "tenth",
        "subject": "Mathematics",
        "num_weeks": 12,
        "start_date": "2024-09-01",
        "additional_objectives": "Enhance problem-solving skills",
        "additional_materials": "Textbook, Notebook",
        "additional_grading_policy": "Weekly tests",
        "additional_class_policy": "Attendance mandatory",
        "custom_course_outline": "Custom outline content"
    }

def test_syllabus_generator_initialization(setup_data):
    generator = SyllabusGenerator(**setup_data)
    assert generator.grade_level == setup_data["grade_level"]
    assert generator.subject == setup_data["subject"]
    assert generator.num_weeks == setup_data["num_weeks"]

    if setup_data["start_date"]:
        assert generator.start_date == datetime.strptime(setup_data["start_date"], "%Y-%m-%d")
    else:
        assert generator.start_date == ""
    assert generator.additional_objectives == setup_data["additional_objectives"]
    assert generator.additional_materials == setup_data["additional_materials"]
    assert generator.additional_grading_policy == setup_data["additional_grading_policy"]
    assert generator.additional_class_policy == setup_data["additional_class_policy"]
    assert generator.custom_course_outline == setup_data["custom_course_outline"]

def test_syllabus_generator_compile(setup_data):
    generator = SyllabusGenerator(**setup_data)
    chain = generator.compile()
    assert chain is not None

def test_syllabus_generator_generate(setup_data):
    generator = SyllabusGenerator(**setup_data)
    result = generator.generate()
    assert result is not None

def test_executor_valid_input(setup_data):
    result = executor(**setup_data)
    assert result is not None

def test_executor_missing_optional_fields(setup_data):
    setup_data.pop("additional_objectives")
    setup_data.pop("additional_materials")
    setup_data.pop("additional_grading_policy")
    setup_data.pop("additional_class_policy")
    setup_data.pop("custom_course_outline")
    result = executor(**setup_data)
    assert result is not None

def test_executor_handle_tool_executor_error(monkeypatch, setup_data):
    def mock_generate(*args, **kwargs):
        raise ToolExecutorError("Mock ToolExecutorError")

    monkeypatch.setattr(SyllabusGenerator, "generate", mock_generate)

    result = executor(**setup_data)
    assert result.status == 500
    assert "Mock ToolExecutorError" in result.message

def test_executor_handle_unexpected_error(monkeypatch, setup_data):
    def mock_generate(*args, **kwargs):
        raise Exception("Mock Exception")

    monkeypatch.setattr(SyllabusGenerator, "generate", mock_generate)

    result = executor(**setup_data)
    assert result.status == 500
    assert "An unexpected error occurred." in result.message