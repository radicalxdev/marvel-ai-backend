# tests/test_core.py
import pytest
from app.features.ai_resistant_assignment_generator.core import executor

def test_executor_valid_input():
    files = ["file1.pdf", "file2.pdf"]
    topic = "Math"
    num_questions = 5
    result = executor(files, topic, num_questions, verbose=False)
    
    assert len(result) == num_questions
    assert isinstance(result, list)

def test_executor_invalid_file():
    with pytest.raises(ValueError):
        executor([], "Math", 5)
