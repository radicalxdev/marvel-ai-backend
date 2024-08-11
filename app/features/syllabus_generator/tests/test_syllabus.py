import time
import pytest
from app.features.syllabus_generator.tests import is_valid_url,Test_Engine,Test_Generator
from langchain_core.prompts import PromptTemplate



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

def test_get_link():
    link = Test_Engine.get_link()
    assert link
    assert isinstance(link, str)
    assert is_valid_url(link)

def test_scrap_data():
    result = Test_Engine.scrap_data()
    assert isinstance(result, list)

def test_build_prompt():
    result = Test_Generator.build_prompt('tests/TestExamples/text.txt')
    assert isinstance(result, PromptTemplate)

def test_course_description():
    result = Test_Generator.course_description()
    assert result
    assert isinstance(result, str)

def test_course_objectives(capture_output):

    description = Test_Generator.read_text_file('tests/TestExamples/description.txt')
    result = Test_Generator.course_objectives(description)
    capture_output(result)
    assert result
    assert isinstance(result, list)

def test_course_outline(capture_output):
    description = Test_Generator.read_text_file('tests/TestExamples/description.txt')
    objectives = Test_Generator.read_text_file('tests/TestExamples/objectives.txt')

    result = Test_Generator.course_outline(description,objectives)
    capture_output(result)
    assert result
    assert isinstance(result, list)
    assert all(isinstance(item, dict) for item in result)
    assert all(item['duration']  for item in result)
    assert all(item['topic'] for item in result)
    assert all(item['subtopics'] for item in result)
    assert all(isinstance(item['subtopics'], list) for item in result)

def test_grading_policy(capture_output):
    outline = Test_Generator.read_text_file('tests/TestExamples/outline.txt')
    result = Test_Generator.grading_policy(outline)
    capture_output(result)
    assert result
    assert isinstance(result, list)
    assert all(isinstance(item, dict) for item in result)
    assert all(item['Component']  for item in result)
    assert all(item['Coefficient'] for item in result)
    assert all(item['Note'] for item in result)

def test_rules_policies(capture_output):
    outline = Test_Generator.read_text_file('tests/TestExamples/outline.txt')
    result = Test_Generator.rules_policies(outline)
    capture_output(result)
    assert result
    assert isinstance(result, dict)
    assert all(isinstance(item, list) for item in result.values())

def test_study_materials(capture_output):
    outline = Test_Generator.read_text_file('tests/TestExamples/outline.txt')
    result = Test_Generator.study_materials(outline)
    capture_output(result)
    assert result
    assert isinstance(result, list)
    assert all(isinstance(item,dict) for item in result)
    assert all(item['material'] for item in result)
    assert all(item['purpose'] for item in result)
