import sys
import os

# Add the root directory to the sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

import pytest
from app.features.text_rewriter.core import executor

def test_executor_with_text():
    input_text = "Romeo and Juliet is a tragic play by William Shakespeare."
    instruction = "simplify"
    result = executor(input_text, instruction)
    assert result is not None  # Adjust based on actual logic

def test_executor_with_invalid_input():
    with pytest.raises(ValueError):
        executor(123, "simplify")