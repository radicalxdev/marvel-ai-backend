import pytest
# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../')))
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())
from app.features.worksheet_generator.core import executor
from app.api.error_utilities import ToolExecutorError
from app.features.worksheet_generator.tools import LoaderError


def test():
    print("Hi Test")

# 1st Test Cases: Test the function of "executor" in core.py.
def test_executor_success():

    files = []  
    topic = "Machine Learning"
    num_questions = 10
    grade_level = "10"
    question_type = "multiple_choice"
    context = "test context"
    verbose = False


    with pytest.raises(ToolExecutorError, match="No files provided for processing"):
        executor(files, topic, num_questions, grade_level, question_type, context, verbose)


# 2nd Test Cases: Test the function of "executor" in core.py.
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
