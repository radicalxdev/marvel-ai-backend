import pytest
from langchain_core.prompts import PromptTemplate
import os
import json
from app.features.syllabus_generator.tools import (
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
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "local-auth.json"

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
    result = course_outline(grade,subject,description,objectives)
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
 
    