import pytest
import os
from unittest.mock import patch, MagicMock
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

def test_read_text_file(test_file):
    test_file_path, test_content = test_file
    result = read_text_file(test_file_path)
    assert result == test_content

@patch('app.features.syllabus_generator.tools.read_text_file')
@patch('langchain_core.prompts.PromptTemplate')
def test_build_prompt(MockPromptTemplate, mock_read_text_file, test_file):
    _, test_content = test_file
    mock_read_text_file.return_value = test_content
    mock_prompt_template_instance = MockPromptTemplate.from_template.return_value
    mock_prompt_template_instance.return_value = test_content

    result = build_prompt('test_file.txt')
    MockPromptTemplate.from_template.assert_called_once_with(test_content)
    assert result == mock_prompt_template_instance

@patch('app.features.syllabus_generator.tools.build_prompt')
@patch('langchain_google_genai.GoogleGenerativeAI')
def test_course_description(MockGoogleGenerativeAI, mock_build_prompt):
    mock_build_prompt.return_value = MagicMock()
    mock_model = MockGoogleGenerativeAI.return_value
    mock_chain = MagicMock()
    mock_model.__or__.return_value = mock_chain
    mock_chain.invoke.return_value = "Generated course description"

    result = course_description(10, "Math")
    mock_chain.invoke.assert_called_once_with({"grade": 10, "subject": "Math", "custom_info": 'None'})
    assert result == "Generated course description"

@patch('app.features.syllabus_generator.tools.build_prompt')
@patch('langchain_google_genai.GoogleGenerativeAI')
def test_course_objectives(MockGoogleGenerativeAI, mock_build_prompt):
    mock_build_prompt.return_value = MagicMock()
    mock_model = MockGoogleGenerativeAI.return_value
    mock_chain = MagicMock()
    mock_model.__or__.return_value = mock_chain
    mock_chain.invoke.return_value = "Generated course objectives"

    result = course_objectives(10, "Math", "Course description")
    mock_chain.invoke.assert_called_once_with({
        "grade": 10, 
        "subject": "Math", 
        "custom_info": 'None', 
        'course_description': 'Course description'
    })
    assert result == "Generated course objectives"

@patch('app.features.syllabus_generator.tools.build_prompt')
@patch('langchain_google_genai.GoogleGenerativeAI')
def test_course_outline(MockGoogleGenerativeAI, mock_build_prompt):
    mock_build_prompt.return_value = MagicMock()
    mock_model = MockGoogleGenerativeAI.return_value
    mock_chain = MagicMock()
    mock_model.__or__.return_value = mock_chain
    mock_chain.invoke.return_value = "Generated course outline"

    result = course_outline(10, "Math", "Course description", "Course objectives")
    mock_chain.invoke.assert_called_once_with({
        "grade": 10, 
        "subject": "Math", 
        "custom_info": 'None', 
        'course_description': 'Course description',
        'course_objectives': 'Course objectives'
    })
    assert result == "Generated course outline"

@patch('app.features.syllabus_generator.tools.build_prompt')
@patch('langchain_google_genai.GoogleGenerativeAI')
def test_grading_policy(MockGoogleGenerativeAI, mock_build_prompt):
    mock_build_prompt.return_value = MagicMock()
    mock_model = MockGoogleGenerativeAI.return_value
    mock_chain = MagicMock()
    mock_model.__or__.return_value = mock_chain
    mock_chain.invoke.return_value = "Generated grading policy"

    result = grading_policy(10, "Math", "Course outline")
    mock_chain.invoke.assert_called_once_with({
        "grade": 10, 
        "subject": "Math", 
        "custom_info": 'None', 
        'course_outline': 'Course outline'
    })
    assert result == "Generated grading policy"

@patch('app.features.syllabus_generator.tools.build_prompt')
@patch('langchain_google_genai.GoogleGenerativeAI')
def test_rules_policies(MockGoogleGenerativeAI, mock_build_prompt):
    mock_build_prompt.return_value = MagicMock()
    mock_model = MockGoogleGenerativeAI.return_value
    mock_chain = MagicMock()
    mock_model.__or__.return_value = mock_chain
    mock_chain.invoke.return_value = "Generated rules and policies"

    result = rules_policies(10, "Math", "Course outline")
    mock_chain.invoke.assert_called_once_with({
        "grade": 10, 
        "subject": "Math", 
        "custom_info": 'None', 
        'course_outline': 'Course outline'
    })
    assert result == "Generated rules and policies"

@patch('app.features.syllabus_generator.tools.build_prompt')
@patch('langchain_google_genai.GoogleGenerativeAI')
def test_study_materials(MockGoogleGenerativeAI, mock_build_prompt):
    mock_build_prompt.return_value = MagicMock()
    mock_model = MockGoogleGenerativeAI.return_value
    mock_chain = MagicMock()
    mock_model.__or__.return_value = mock_chain
    mock_chain.invoke.return_value = "Generated study materials"

    result = study_materials(10, "Math", "Course outline")
    mock_chain.invoke.assert_called_once_with({
        "grade": 10, 
        "subject": "Math", 
        "custom_info": 'None', 
        'course_outline': 'Course outline'
    })
    assert result == "Generated study materials"

def test_final_output():
    course_desc = "Course description"
    course_obj = "Course objectives"
    course_out = "Course outline"
    grading_pol = "Grading policy"
    rules_pol = "Rules and policies"
    study_mat = "Study materials"
    
    result = final_output(course_desc, course_obj, course_out, grading_pol, rules_pol, study_mat)
    
    expected_output = (
        f"#Course Description\n{course_desc}\n\n"
        f"#Course Objectives\n{course_obj}\n\n"
        f"#Course Outline\n{course_out}\n\n"
        f"#Grading Policy\n{grading_pol}\n\n"
        f"#Class Rules\n{rules_pol}\n\n"
        f"#Study Materials\n{study_mat}\n\n"
    )
    
    assert result == expected_output

if __name__ == '__main__':
    pytest.main()