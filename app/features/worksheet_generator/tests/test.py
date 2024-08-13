from evaluator import AnswerEvaluator

import pytest
from unittest.mock import patch, MagicMock

from app.services.tool_registry import ToolFile
from app.services.logger import setup_logger
from app.features.worksheet_generator.tools import WorksheetBuilder
from app.features.quizzify.tools import LocalFileLoader
from app.api.error_utilities import LoaderError, ToolExecutorError
logger = setup_logger()



if __name__ == "__main__":
    # Download stopwords if not already downloaded
    #nltk.download('punkt')
    #nltk.download('stopwords')
    evaluator = AnswerEvaluator()

    # Example usage
    question = "What is the capital of France?"
    ground_truth = "Paris"
    given_answer = "The capital of France is Paris."

    accuracy, match_type = evaluator.evaluate_answer(given_answer, ground_truth)
    print(f"Accuracy: {accuracy}, Match Type: {match_type}")

    question = "Explain the theory of relativity."
    ground_truth = "The theory of relativity, formulated by Albert Einstein, revolutionized the way we understand space, time, and gravity. It consists of two theories: special relativity and general relativity."
    given_answer = "Einstein's theory of relativity changed our understanding of space, time, and gravity. It includes special and general relativity."

    accuracy, match_type = evaluator.evaluate_answer(given_answer, ground_truth)
    print(f"Accuracy: {accuracy}, Match Type: {match_type}")

    ground_truth = 'a'
    given_answer = 'a'

    accuracy, match_type = evaluator.evaluate_answer(given_answer, ground_truth)
    print(f"Accuracy: {accuracy}, Match Type: {match_type}")