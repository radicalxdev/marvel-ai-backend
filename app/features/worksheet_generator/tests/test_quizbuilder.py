import sys
import os
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

import pytest
from unittest.mock import MagicMock, patch, mock_open
from fastapi import UploadFile
from pydantic import BaseModel
from io import BytesIO
from pypdf import PdfReader
from app.features.worksheet_generator.tools import (
    QuizBuilder, GoogleGenerativeAI, JsonOutputParser, 
    PromptTemplate, QuizQuestion, QuestionChoice, TextOrPDFLoader, 
    QuestionGenerator, RunnablePassthrough
)

@pytest.fixture
def mock_vectorstore():
    return MagicMock()

@pytest.fixture
def mock_quiz_builder(mock_vectorstore):
    return QuizBuilder(
        vectorstore=mock_vectorstore,
        topic="Artificial Intelligence",
        prompt="Generate quiz questions about {topic}",
        model=GoogleGenerativeAI(model="gemini-1.0-pro"),
        parser=JsonOutputParser(pydantic_object=QuizQuestion),
        verbose=True
    )

def test_quiz_builder_init(mock_vectorstore):
    quiz_builder = QuizBuilder(
        vectorstore=mock_vectorstore,
        topic="Artificial Intelligence"
    )
    assert quiz_builder.topic == "Artificial Intelligence"
    assert isinstance(quiz_builder.model, GoogleGenerativeAI)
    assert isinstance(quiz_builder.parser, JsonOutputParser)

def test_quiz_builder_compile(mock_quiz_builder):
    chain = mock_quiz_builder.compile()
    assert chain is not None

def test_quiz_builder_validate_response_valid(mock_quiz_builder):
    valid_response = {
        "question": "What is AI?",
        "choices": {"A": "Artificial Intelligence", "B": "Automated Intelligence"},
        "answer": "A",
        "explanation": "AI stands for Artificial Intelligence."
    }
    result = mock_quiz_builder.validate_response(valid_response)
    assert result == True

def test_quiz_builder_validate_response_invalid(mock_quiz_builder):
    invalid_response = {
        "question": "What is AI?",
        "choices": {"A": "Artificial Intelligence"},
    }
    result = mock_quiz_builder.validate_response(invalid_response)
    assert result == False

def test_quiz_builder_format_choices(mock_quiz_builder):
    choices = {"A": "Option A", "B": "Option B"}
    formatted_choices = mock_quiz_builder.format_choices(choices)
    assert formatted_choices == [{"key": "A", "value": "Option A"}, {"key": "B", "value": "Option B"}]

def test_quiz_builder_create_questions(mock_quiz_builder):
    with patch.object(mock_quiz_builder, 'compile') as mock_compile:
        mock_chain = MagicMock()
        mock_chain.invoke = MagicMock(return_value={
            "question": "What is AI?",
            "choices": {"A": "Artificial Intelligence", "B": "Automated Intelligence"},
            "answer": "A",
            "explanation": "AI stands for Artificial Intelligence."
        })
        mock_compile.return_value = mock_chain

        questions = mock_quiz_builder.create_questions(num_questions=5)
        assert len(questions) == 1
        assert questions[0]["question"] == "What is AI?"

def test_text_or_pdf_loader_text():
    loader = TextOrPDFLoader(text="Sample text")
    content = loader.load()
    assert content == "Sample text"



def test_quiz_question_model():
    question = QuizQuestion(
        question="What is AI?",
        choices=[QuestionChoice(key="A", value="Artificial Intelligence"), QuestionChoice(key="B", value="Automated Intelligence")],
        answer="A",
        explanation="AI stands for Artificial Intelligence."
    )
    assert question.question == "What is AI?"
    assert len(question.choices) == 2
    assert question.answer == "A"
    assert question.explanation == "AI stands for Artificial Intelligence."


