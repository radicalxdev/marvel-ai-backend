import pytest
from langchain_core.prompts import PromptTemplate
from app.features.syllabus_generator.tools import Search_engine,Syllabus_generator
from dotenv import load_dotenv
import os
import re
from pathlib import Path
import time

env_path = Path(__file__).resolve().parents[3] / '.env'

# Load the .env file
load_dotenv(dotenv_path=env_path)

API_KEY = os.getenv('API_KEY')
SEARCH_ENGINE_ID = os.getenv('SEARCH_ENGINE_ID')
grade = 'university'
subject = 'Computer science'
Syllabus_type = 'Exam-based'

Test_Engine = Search_engine(grade,subject,Syllabus_type,API_KEY,SEARCH_ENGINE_ID)
Test_Generator = Syllabus_generator(grade,subject,API_KEY,SEARCH_ENGINE_ID)

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "local-auth.json"

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
    time.sleep(1.5) 
    yield
    # Teardown code: Add a delay after the test
    print("Teardown: Adding delay after test")
    time.sleep(1.5)  

def is_valid_url(url):
    pattern = re.compile(r'^https?://(www\.)?([\w\.-]+)(/[\w\-/]*)?$')
    return bool(pattern.match(url))

def test_scrap_data():
    link = Test_Engine.scrap_data()
    assert (link and 
            isinstance(link, str) and 
            is_valid_url(link))
    
def test_get_web_results():
    
    result = Test_Engine.get_web_results()
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
    web_search = Test_Generator.read_text_file('tests/TestExamples/search.txt')
    
    result = Test_Generator.course_outline(description,objectives)
    capture_output(result)
    assert ( result and 
             isinstance(result, list) and 
             isinstance(result[0], dict) and 
             result[0]['week'] and
             result[0]['topic'] )
    
def test_grading_policy(capture_output):
    outline = Test_Generator.read_text_file('tests/TestExamples/outline.txt')
    result = Test_Generator.grading_policy(outline)
    capture_output(result)
    assert result and isinstance(result, str)
    
def test_rules_policies(capture_output):
    outline = Test_Generator.read_text_file('tests/TestExamples/outline.txt')
    result = Test_Generator.rules_policies(outline)
    capture_output(result)
    assert result and isinstance(result, list)
    
def test_study_materials(capture_output):
    outline = Test_Generator.read_text_file('tests/TestExamples/outline.txt')
    result = Test_Generator.study_materials(outline)
    capture_output(result)
    assert ( result and 
             isinstance(result, list) and 
             isinstance(result[0], dict) and 
             result[0]['material'] and
             result[0]['purpose'] )
 
    