import pytest
from app.features.worksheet_generator.core import executor
from app.api.error_utilities import ToolExecutorError
from app.features.worksheet_generator.tools import LoaderError

def test_executor_success():

    files = []  
    topic = "Machine Learning"
    num_questions = 10
    grade_level = "10"
    question_type = "multiple_choice"
    context = "test context"
    verbose = False

    try:
        result = executor(files, topic, num_questions, grade_level, question_type, context, verbose)
    except ToolExecutorError:
        pytest.fail("executor raised ToolExecutorError unexpectedly")

    assert result is not None
    assert len(result) == num_questions

def test_executor_failure_loader_error(monkeypatch):

    files = []  
    topic = "InvalidTopic"
    num_questions = 10
    grade_level = "10"
    question_type = "multiple_choice"
    context = "test context"
    verbose = False

    def mock_pipeline(files):
        raise LoaderError("Mock loader error")
    
    monkeypatch.setattr('app.features.worksheet_generator.tools.RAGpipeline.__call__', mock_pipeline)

    with pytest.raises(ToolExecutorError):
        executor(files, topic, num_questions, grade_level, question_type, context, verbose)
