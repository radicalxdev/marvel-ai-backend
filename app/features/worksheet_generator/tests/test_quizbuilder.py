import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../')))

import pytest
from unittest.mock import MagicMock, patch
from app.features.worksheet_generator.tools import QuizBuilder
from langchain_chroma import Chroma
from langchain_google_vertexai import VertexAI

class TestQuizBuilder:
    @pytest.fixture
    def mock_vectorstore(self):
        return MagicMock(spec=Chroma)

    @pytest.fixture
    def mock_vertexai(self):
        return MagicMock(spec=VertexAI)

    @pytest.fixture
    def quiz_builder(self, mock_vectorstore, mock_vertexai):
        topic = "Sample Topic"
        return QuizBuilder(vectorstore=mock_vectorstore, topic=topic, model=mock_vertexai)

    @patch("app.features.worksheet_generator.tools.read_text_file", return_value="Sample Prompt")
    def test_compile(self, mock_read_text_file, quiz_builder):
        chain = quiz_builder.compile()
        assert chain is not None
        assert quiz_builder.prompt == "Sample Prompt"

    def test_validate_response_valid(self, quiz_builder):
        response = {
            "question": "Sample question?",
            "choices": {"A": "Option 1", "B": "Option 2"},
            "answer": "A",
            "explanation": "Sample explanation"
        }
        assert quiz_builder.validate_response(response) is True

    def test_validate_response_invalid(self, quiz_builder):
        response = {
            "question": "Sample question?",
            "choices": {"A": "Option 1", "B": "Option 2"},
            # Missing 'answer' and 'explanation'
        }
        assert quiz_builder.validate_response(response) is False

    def test_format_choices(self, quiz_builder):
        choices = {"A": "Option 1", "B": "Option 2"}
        formatted_choices = quiz_builder.format_choices(choices)
        assert formatted_choices == [{"key": "A", "value": "Option 1"}, {"key": "B", "value": "Option 2"}]

    @patch.object(QuizBuilder, 'compile', return_value=MagicMock())
    @patch.object(QuizBuilder, 'validate_response', return_value=True)
    @patch.object(QuizBuilder, 'format_choices', return_value=[{"key": "A", "value": "Option 1"}])
    @patch("app.features.worksheet_generator.tools.read_text_file", return_value="Sample Prompt")
    def test_create_questions(self, mock_read_text_file, mock_compile, mock_validate_response, mock_format_choices, quiz_builder):
        mock_chain = mock_compile.return_value
        mock_chain.invoke.return_value = {
            "question": "Sample question?",
            "choices": {"A": "Option 1"},
            "answer": "A",
            "explanation": "Sample explanation"
        }

        questions = quiz_builder.create_questions(num_questions=3)
        assert len(questions) == 3
        for question in questions:
            assert question["question"] == "Sample question?"
            assert question["choices"] == [{"key": "A", "value": "Option 1"}]
            assert question["answer"] == "A"
            assert question["explanation"] == "Sample explanation"
