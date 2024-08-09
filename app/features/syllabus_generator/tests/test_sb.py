import os
import sys
import unittest
from unittest import mock
from unittest.mock import MagicMock, Mock, mock_open, patch

import pytest
import pytest_mock
from dotenv import load_dotenv
from features.syllabus_generator.tools import (
    SyllabusBuilder,
    SyllabusModel,
    read_text_file,
)
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import GoogleGenerativeAI
from pydantic import BaseModel, Field, ValidationError

# Make sure all correct paths exist in PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

# needs correct API keys to run tests
load_dotenv()


@pytest.fixture
def sb():
    return SyllabusBuilder(subject="Math", grade_level="grade 10", verbose=True)


def test_invalid_input():
    with pytest.raises(ValueError):
        SyllabusBuilder(subject="", grade_level=10)

    with pytest.raises(ValueError):
        SyllabusBuilder(subject="Biology", grade_level=None)


def test_create_prompt_temp_with_mocked_read_text_file(sb):
    with patch("features.syllabus_generator.tools.read_text_file") as mock_method:
        mock_method.return_value = "high school assessment grading policy"
        sb._create_prompt_temp()
        assert sb.grade_level_assessments == "high school assessment grading policy"

    with patch("features.syllabus_generator.tools.read_text_file") as mock_method:
        mock_method.return_value = "Elementary school assessment grading policy"
        sb_elementary = SyllabusBuilder(subject="Math", grade_level="K12")
        sb_elementary._create_prompt_temp()
        assert (
            sb_elementary.grade_level_assessments
            == "Elementary school assessment grading policy"
        )

    with patch("features.syllabus_generator.tools.read_text_file") as mock_method:
        mock_method.return_value = "Primary school assessment grading policy"
        sb_primary = SyllabusBuilder(subject="Math", grade_level="grade 5")
        sb_primary._create_prompt_temp()
        assert (
            sb_primary.grade_level_assessments
            == "Primary school assessment grading policy"
        )

    with patch("features.syllabus_generator.tools.read_text_file") as mock_method:
        mock_method.return_value = "Middle school assessment grading policy"
        sb_middle = SyllabusBuilder(subject="Math", grade_level="grade 8")
        sb_middle._create_prompt_temp()
        assert (
            sb_middle.grade_level_assessments
            == "Middle school assessment grading policy"
        )

    with patch("features.syllabus_generator.tools.read_text_file") as mock_method:
        mock_method.return_value = "University assessment grading policy"
        sb_uni = SyllabusBuilder(subject="Math", grade_level="university")
        sb_uni._create_prompt_temp()
        assert sb_uni.grade_level_assessments == "University assessment grading policy"


@patch.object(SyllabusBuilder, "_create_custom_promptTemp")
@patch.object(SyllabusBuilder, "_create_prompt_temp")
def test_compile(mock_create_prompt_temp, mock_create_custom_promptTemp):
    mock_custom_prompt_instance = MagicMock(spec=PromptTemplate)
    mock_create_custom_promptTemp.return_value = mock_custom_prompt_instance

    mock_syllabus_prompt_instance = MagicMock(spec=PromptTemplate)
    mock_create_prompt_temp.return_value = mock_syllabus_prompt_instance

    sb = SyllabusBuilder(subject="Mathematics", grade_level="Grade 5", verbose=True)
    # Call the compile method with type "customisation"
    chain_customisation = sb._compile("customisation")
    mock_create_custom_promptTemp.assert_called_once()

    chain_syllabus = sb._compile("syllabus")
    mock_create_prompt_temp.assert_called_once()


def test_validate_respose_valid(sb):
    valid_response = {
        "title": "Sample Syllabus Title",
        "overview": "Sample overview of the syllabus content.",
        "objectives": [
            "Define the key terms associated with...",
            "Describe the cardiac cycle...",
        ],
        "policies_and_exceptions": {
            "attendance_requirements": "Sample attendance requirements...",
            "make_up_work": "Sample make-up work policy...",
        },
        "grade_level_assessments": {
            "assessment_components": {
                "assignments": 20,
                "exams": 25,
                "projects": 25,
                "presentations": 15,
                "participation": 15,
            },
            "grade_scale": {
                "A": "90-100%",
                "B": "80-89%",
                "C": "70-79%",
                "D": "60-69%",
                "F": "Below 60%",
            },
        },
        "required_materials": {
            "recommended_books": ["book 1", "book 2", "book 3"],
            "required_items": [
                "paint",
                "paintbrush",
                "pencil",
                "eraser",
                "notebooks" "sharpies",
                "crayons",
                "black ink pen",
                "ruler",
            ],
        },
        "additional_information": {
            "Visual aids": ["Diagram of the cardiovascular system", ...],
            "Resources": ["Electrocardiography for Healthcare Professionals"],
        },
    }

    # Call the validate_response method
    is_valid = sb._validate_response(valid_response)

    # Assert that the response is valid
    assert is_valid is True


def test_validate_response_invalid(sb):
    # Create an invalid response dictionary (missing objectives)
    invalid_response = {
        "title": "Sample Syllabus Title",
        "overview": "Sample overview of the syllabus content.",
        "policies_and_exceptions": {
            "attendance_requirements": "Sample attendance requirements...",
            "make_up_work": "Sample make-up work policy...",
        },
        # make grade_components str
        "grade_level_assessments": {
            "assessment_components": {
                "assignments": "20%",
                "exams": "25%",
                "projects": "25%",
                "presentations": "15%",
                "participation": "15%",
            },
            "grade_scale": {
                "A": "90-100%",
                "B": "80-89%",
                "C": "70-79%",
                "D": "60-69%",
                "F": "Below 60%",
            },
        },
        # missing required material
        "additional_information": {
            "Visual aids": ["Diagram of the cardiovascular system"],
            "Resources": ["Electrocardiography for Healthcare Professionals"],
        },
    }

    # Call the validate_response method
    is_valid = sb._validate_response(invalid_response)

    # Assert that the response is invalid
    assert is_valid is False


def test_valid_model():
    # Example of a valid input dictionary
    valid_input = {
        "title": "Sample Syllabus Title",
        "overview": "Sample overview of the syllabus content.",
        "objectives": [
            "Define the key terms associated with...",
            "Describe the cardiac cycle...",
        ],
        "policies_and_exceptions": {
            "attendance_requirements": "Sample attendance requirements...",
            "make_up_work": "Sample make-up work policy...",
        },
        "grade_level_assessments": {
            "assessment_components": {
                "assignments": 20,
                "exams": 25,
                "projects": 25,
                "presentations": 15,
                "participation": 15,
            },
            "grade_scale": {
                "A": "90-100%",
                "B": "80-89%",
                "C": "70-79%",
                "D": "60-69%",
                "F": "Below 60%",
            },
        },
        "additional_information": {
            "Visual aids": ["Diagram of the cardiovascular system"],
            "Additional Resources": [
                "Electrocardiography for Healthcare Professionals"
            ],
        },
        "required_materials": {
            "recommended_books": ["book 1", "book 2", "book 3"],
            "required_items": [
                "paint",
                "paintbrush",
                "pencil",
                "eraser",
                "notebooks" "sharpies",
                "crayons",
                "black ink pen",
                "ruler",
            ],
        },
    }

    # Create an instance of the model with the valid input
    model_instance = SyllabusModel(**valid_input)

    # Assert that the model instance is valid (should not raise ValidationError)
    assert model_instance.title == "Sample Syllabus Title"
    assert model_instance.objectives == valid_input["objectives"]
    # Add more assertions for other fields as needed


def test_invalid_model():
    # Example of an invalid input dictionary (missing required fields)
    invalid_input = {
        "title": "Sample Syllabus Title",
        # Missing "overview", "objectives", "policies_and_exceptions", "grade_level_assessments", "additional_information" and "required material"
    }

    # Try to create an instance of the model with the invalid input
    with pytest.raises(ValidationError):
        SyllabusModel(**invalid_input)


if __name__ == "__main__":
    # print(get_test_prompt())
    print(os.environ["PYTHONPATH"])
