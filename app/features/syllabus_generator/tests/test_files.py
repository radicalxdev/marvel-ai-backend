import pytest
from app.features.syllabus_generator.tools import PDFGenerator,WordGenerator
from app.features.syllabus_generator.tests import data,grade,subject
from io import BytesIO

def test_generate_pdf():
    Gen = PDFGenerator(grade,subject)
    result = Gen.generate_pdf(data)
    assert result
    assert isinstance(result, BytesIO)

def test_generate_word():
    Gen = WordGenerator(grade,subject)
    result = Gen.generate_word(data)
    assert result
    assert isinstance(result, BytesIO)
