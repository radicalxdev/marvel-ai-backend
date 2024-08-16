#import pytest
from app.features.worksheet_generator.tools import *
#from app.features.worksheet_generator.core import *

def test_document_processor_initialization():
    processor = DocumentProcessor()
    assert processor.pages == []

def test_embedding_client_initialization():
    embed_client = EmbeddingClient(model_name="textembedding-gecko@003", project="kaidev-431918", location="us-central1")
    assert embed_client.client is not None

def test_quiz_generator_initialization():
    generator = QuizGenerator(topic="AI", num_questions=5, vectorstore=None)
    assert generator.topic == "AI"
    assert generator.num_questions == 5

