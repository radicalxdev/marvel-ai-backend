import pytest
from app.features.connect_with_them.tools import CWTRecommendationGenerator, validate_input
from unittest.mock import patch

def test_validate_input_success():
    """Test validate_input function for successful input validation."""
    subject = "Science"
    students_description = "Students interested in biology and chemistry."
    assert validate_input(subject, students_description) is True

def test_validate_input_failure():
    """Test validate_input function for input validation failure scenarios."""
    # Check validation fails for empty subject
    assert validate_input("", "Some description") is False
    # Check validation fails for empty student description
    assert validate_input("Math", "") is False
    # Check validation fails for both inputs empty
    assert validate_input("", "") is False

def test_CWTRecommendationGenerator_initialization():
    """Test initialization of the CWTRecommendationGenerator class."""
    grade = "4th"
    subject = "History"
    students_description = "Students who love stories and historical events."
    
    generator = CWTRecommendationGenerator(grade, subject, students_description)
    # Assert that the properties are set correctly during initialization
    assert generator.grade == grade
    assert generator.subject == subject
    assert generator.students_description == students_description