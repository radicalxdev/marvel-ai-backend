import pytest
from langchain_core.prompts import PromptTemplate
from app.features.syllabus_generator.tools import (
    scrap_data,
    get_table_from_link,
    read_text_file, 
    build_prompt, 
    course_description, 
    course_objectives, 
    course_outline, 
    grading_policy, 
    rules_policies, 
    study_materials, 
    final_output
)
from dotenv import load_dotenv
import os
import re
from pathlib import Path

env_path = Path(__file__).resolve().parents[3] / '.env'

# Load the .env file
load_dotenv(dotenv_path=env_path)

#Retrieve the value of the environment variable
API_KEY = os.getenv('API_KEY')
SEARCH_ENGINE_ID = os.getenv('SEARCH_ENGINE_ID')

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "local-auth.json"

def is_valid_url(url):
    pattern = re.compile(r'^https?://(www\.)?([\w\.-]+)(/[\w\-/]*)?$')
    return bool(pattern.match(url))

def test_scrap_data():
    grade = 'university'
    subject = 'Computer science'
    
    link = scrap_data(grade,subject,API_KEY,SEARCH_ENGINE_ID)
    assert (link and 
            isinstance(link, str) and 
            is_valid_url(link))
    
def test_get_table_from_link():
    grade = 'university'
    subject = 'Computer science'
    
    result = get_table_from_link(grade,subject,API_KEY,SEARCH_ENGINE_ID)
    assert result and isinstance(result, str)

def test_read_text_file():
    result = read_text_file('tests/TestExamples/text.txt')
    assert result == 'this is a test string'

def test_build_prompt():
    result = build_prompt('tests/TestExamples/text.txt')
    assert isinstance(result, PromptTemplate)
    
def test_course_description():
    grade = 'university'
    subject = 'Computer science'
    
    result = course_description(grade,subject)
    assert result and isinstance(result, str)
    
def test_course_objectives():
    description = read_text_file('tests/TestExamples/description.txt')
    grade = 'university'
    subject = 'Computer science'
    result = course_objectives(grade,subject,description)
    assert result and isinstance(result, list)
    
def test_course_outline():
    grade = 'university'
    subject = 'Computer science'
    description = read_text_file('tests/TestExamples/description.txt')
    objectives = read_text_file('tests/TestExamples/objectives.txt')
    web_search = read_text_file('tests/TestExamples/search.txt')
    result = course_outline(grade,subject,description,objectives,web_search)
    assert ( result and 
             isinstance(result, list) and 
             isinstance(result[0], dict) and 
             result[0]['week'] and
             result[0]['topic'] )
    
def test_grading_policy():
    grade = 'university'
    subject = 'Computer science'
    outline = read_text_file('tests/TestExamples/outline.txt')
    result = grading_policy(grade,subject,outline)
    assert result and isinstance(result, str)
    
def test_rules_policies():
    grade = 'university'
    subject = 'Computer science'
    outline = read_text_file('tests/TestExamples/outline.txt')
    result = rules_policies(grade,subject,outline)
    assert result and isinstance(result, list)
    
def test_study_materials():
    grade = 'university'
    subject = 'Computer science'
    outline = read_text_file('tests/TestExamples/outline.txt')
    result = study_materials(grade,subject,outline)
    assert ( result and 
             isinstance(result, list) and 
             isinstance(result[0], dict) and 
             result[0]['material'] and
             result[0]['purpose'] )
 
    