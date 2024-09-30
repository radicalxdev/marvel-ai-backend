import pytest
from app.features.connect_with_them.core import executor
from unittest.mock import patch

# Sample input for testing
grade = "5th"
subject = "Mathematics"
students_description = "A group of diverse learners with varying interests in technology and sports."

def test_executor_success():
    """Test the executor function for successful recommendation generation."""
    with patch('app.features.connect_with_them.core.validate_input') as mock_validate, \
         patch('app.features.connect_with_them.core.CWTRecommendationGenerator') as mock_generator:
        
        # Mock the input validation to always return True
        mock_validate.return_value = True
        # Mock the generator to return sample recommendations
        mock_generator.return_value = {"recommendations": ["Recommendation 1", "Recommendation 2", "Recommendation 3"]}
        
        # Execute the function
        result = executor(grade, subject, students_description)
        # Assert the expected result matches the mocked output
        assert result == {"recommendations": ["Recommendation 1", "Recommendation 2", "Recommendation 3"]}
        # Ensure validate_input was called with correct arguments
        mock_validate.assert_called_once_with(subject, students_description)

def test_executor_input_validation_failure():
    """Test the executor function for handling input validation failure."""
    with patch('app.features.connect_with_them.core.validate_input', return_value=False):
        # Expect a ValueError to be raised when validation fails
        with pytest.raises(ValueError, match="Input validation failed"):
            executor(grade, subject, students_description)

def test_executor_logging_on_exception():
    """Test that the executor function logs errors appropriately on exceptions."""
    with patch('app.features.connect_with_them.core.validate_input', return_value=True), \
         patch('app.features.connect_with_them.core.CWTRecommendationGenerator', side_effect=Exception("Test Exception")), \
         patch('app.features.connect_with_them.core.logger') as mock_logger:
        
        # Expect a ValueError to be raised and log the error message
        with pytest.raises(ValueError, match="Error in executor: Test Exception"):
            executor(grade, subject, students_description)
        
        # Verify that the error was logged
        mock_logger.error.assert_called_once_with("Error in executor: Test Exception")
