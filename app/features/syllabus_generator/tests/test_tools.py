import unittest
import os
from unittest.mock import patch, MagicMock
from tools import (
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
class TestFunctions(unittest.TestCase):

    def setUp(self):
        # Setup a test file
        self.test_file_name = 'test_file.txt'
        self.test_content = 'Hello, world!'
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.test_file_path = os.path.join(script_dir, self.test_file_name)
        with open(self.test_file_path, 'w') as f:
            f.write(self.test_content)


    def tearDown(self):
        # Clean up the test file after each test

        os.remove(self.test_file_path)

    def test_read_text_file(self):
        result = read_text_file(self.test_file_name)
        self.assertEqual(result, self.test_content)

    @patch('your_module.read_text_file')
    @patch('your_module.PromptTemplate')
    def test_build_prompt(self, MockPromptTemplate, mock_read_text_file):
        mock_read_text_file.return_value = self.test_content
        mock_prompt_template_instance = MockPromptTemplate.from_template.return_value
        mock_prompt_template_instance.return_value = self.test_content

        result = build_prompt(self.test_file_name)
        MockPromptTemplate.from_template.assert_called_once_with(self.test_content)
        self.assertEqual(result, mock_prompt_template_instance)

    @patch('your_module.build_prompt')
    @patch('your_module.GoogleGenerativeAI')
    def test_course_description(self, MockGoogleGenerativeAI, mock_build_prompt):
        mock_build_prompt.return_value = MagicMock()
        mock_model = MockGoogleGenerativeAI.return_value
        mock_chain = MagicMock()
        mock_model.__or__.return_value = mock_chain
        mock_chain.invoke.return_value = "Generated course description"

        result = course_description(10, "Math")
        mock_chain.invoke.assert_called_once_with({"grade": 10, "subject": "Math", "custom_info": 'None'})
        self.assertEqual(result, "Generated course description")

    @patch('your_module.build_prompt')
    @patch('your_module.GoogleGenerativeAI')
    def test_course_objectives(self, MockGoogleGenerativeAI, mock_build_prompt):
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
        self.assertEqual(result, "Generated course objectives")

    @patch('your_module.build_prompt')
    @patch('your_module.GoogleGenerativeAI')
    def test_course_outline(self, MockGoogleGenerativeAI, mock_build_prompt):
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
        self.assertEqual(result, "Generated course outline")

    @patch('your_module.build_prompt')
    @patch('your_module.GoogleGenerativeAI')
    def test_grading_policy(self, MockGoogleGenerativeAI, mock_build_prompt):
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
        self.assertEqual(result, "Generated grading policy")

    @patch('your_module.build_prompt')
    @patch('your_module.GoogleGenerativeAI')
    def test_rules_policies(self, MockGoogleGenerativeAI, mock_build_prompt):
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
        self.assertEqual(result, "Generated rules and policies")

    @patch('your_module.build_prompt')
    @patch('your_module.GoogleGenerativeAI')
    def test_study_materials(self, MockGoogleGenerativeAI, mock_build_prompt):
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
        self.assertEqual(result, "Generated study materials")

    def test_final_output(self):

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
        
        self.assertEqual(result, expected_output)

if __name__ == '__main__':
    unittest.main()