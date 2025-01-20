import pytest
from app.features.notes_generator.core import executor

def test_executor_with_text():
    content = "Photosynthesis is a process used by plants to convert sunlight into energy."
    focus = "Summarize the key steps of photosynthesis."
    input_type = "text"
    result = executor(content, focus, input_type)
    assert result is not None  # Adjust based on actual logic

def test_executor_with_invalid_input_type():
    content = "Some content"
    focus = "Some focus"
    input_type = "invalid"
    with pytest.raises(ValueError):
        executor(content, focus, input_type)