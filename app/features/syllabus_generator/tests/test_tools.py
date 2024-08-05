# Standard library imports
import os
import re
import time
from pathlib import Path
from io import BytesIO
# Third-party imports
from dotenv import load_dotenv, find_dotenv
import pytest

# Application-specific imports
from app.features.syllabus_generator.tools import Search_engine, Syllabus_generator,Doc_Generator
from langchain_core.prompts import PromptTemplate
from app.features.syllabus_generator.tests.TestExamples.Data import data

load_dotenv(find_dotenv())
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "local-auth.json"

API_KEY = os.getenv('API_KEY')
SEARCH_ENGINE_ID = os.getenv('SEARCH_ENGINE_ID')

grade = 'university'
subject = 'Computer science'
Syllabus_type = 'Exam-based'
instructions = 'None'

Test_Engine = Search_engine(grade,subject,API_KEY,SEARCH_ENGINE_ID)
Test_Generator = Syllabus_generator(grade,subject,Syllabus_type,instructions,API_KEY,SEARCH_ENGINE_ID)
Doc_Generator = Doc_Generator(grade,subject)

@pytest.fixture
def capture_output(request):
    test_output = []
    def capture(value):
        test_output.append(value)
    yield capture
    print(f"\nTeardown: Output of {request.node.name} is {test_output}")

@pytest.fixture(autouse=True)
def add_delay():
    # Setup code: Add a delay before the test
    print("\nSetup: Adding delay before test")
    time.sleep(2.5)
    yield
    # Teardown code: Add a delay after the test
    print("Teardown: Adding delay after test")
    time.sleep(2.5)

def is_valid_url(url):
    pattern = re.compile(r'^https?://(www\.)?([\w\.-]+)(/[\w\-/]*)?$')
    return bool(pattern.match(url))

def test_get_link():
    link = Test_Engine.get_link()
    assert (link and
            isinstance(link, str) and
            is_valid_url(link))

def test_scrap_data():

    result = Test_Engine.scrap_data()
    assert result and isinstance(result, list)

def test_build_prompt():
    result = Test_Generator.build_prompt('tests/TestExamples/text.txt')
    assert isinstance(result, PromptTemplate)

def test_course_description():
    result = Test_Generator.course_description()
    assert result and isinstance(result, str)

def test_course_objectives(capture_output):

    description = Test_Generator.read_text_file('tests/TestExamples/description.txt')
    result = Test_Generator.course_objectives(description)
    capture_output(result)
    assert result and isinstance(result, list)

def test_course_outline(capture_output):
    description = Test_Generator.read_text_file('tests/TestExamples/description.txt')
    objectives = Test_Generator.read_text_file('tests/TestExamples/objectives.txt')

    result = Test_Generator.course_outline(description,objectives)
    capture_output(result)
    assert ( result and
             isinstance(result, list) and
             isinstance(result[0], dict) and
             result[0]['duration'] and
             result[0]['topic'] and
             result[0]['subtopics'] and
             isinstance(result[0]['subtopics'], list) )

def test_grading_policy(capture_output):
    outline = Test_Generator.read_text_file('tests/TestExamples/outline.txt')
    result = Test_Generator.grading_policy(outline)
    capture_output(result)
    assert ( result and
             isinstance(result, list) and
             isinstance(result[0], dict) and
             result[0]['Component'] and
             result[0]['Coefficient'] and
             result[0]['Note'] )

def test_rules_policies(capture_output):
    outline = Test_Generator.read_text_file('tests/TestExamples/outline.txt')
    result = Test_Generator.rules_policies(outline)
    capture_output(result)
    assert ( result and
             isinstance(result, dict) )

def test_study_materials(capture_output):
    outline = Test_Generator.read_text_file('tests/TestExamples/outline.txt')
    result = Test_Generator.study_materials(outline)
    capture_output(result)
    assert ( result and
             isinstance(result, list) and
             isinstance(result[0], dict) and
             result[0]['material'] and
             result[0]['purpose'] )

def test_generate_pdf():
    result = Doc_Generator.generate_pdf(data)
    assert result and isinstance(result, BytesIO)

def test_generate_word():
    result = Doc_Generator.generate_word(data)
    assert result and isinstance(result, BytesIO)
