import os
import sys
import unittest
from unittest import mock
from unittest.mock import patch, mock_open, MagicMock
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_google_genai import GoogleGenerativeAI
from pydantic import BaseModel, Field, ValidationError
from typing import List, Dict
import os

from services.logger import setup_logger
from features.syllabus_generator.tools import (
    SyllabusBuilder,
    SyllabusModel,
    read_text_file,
)


default_config = {
    "model": GoogleGenerativeAI(model="gemini-1.0-pro"),
    "parser": JsonOutputParser(pydantic_object=SyllabusModel),
}

test_prompt = """You are a teacher for grade: {grade_level}.

Follow these instructions to create a {subject} syllabus for your students:
1. Generate a range of topics that should be mastered by students.
2. Generate a list of learning objectives for each topic that show a students understanding.
3. {grade_level_assessments}

Use the provided additional notes to further tailor the syllabus as needed:
        {customisation}

You must respond as a JSON object: 
{format_instructions}
"""

custom_test_prompt = """syllabus : {syllabus}
customise only the necessary sections of the syllabus with the user requirements mentioned in {customisation} and leave other sections unchanged from its initial value. Add any additional information in a new field and name it "additional information" and apart from adding the new field do not change the initial structure of the syllabus.
You must respond as a JSON object: 
{format_instructions}

"""

assessment_prompt = """Create a grading policy for primary school students (grades 1-6). The policy should reflect a balance between academic achievement and developmental progress. Include the following elements:
Assessment Components: Detail how students will be assessed through assignments, quizzes, projects, and participation. Example weightage: 30% assignments, 25% quizzes, 25% projects, 20% participation.
Grade Scale: Use a clear scale with descriptive terms:
  1. Outstanding (O)
  2. Proficient (P)
  3. Basic (B)
  4. Needs Improvement (N)
Performance Expectations: Emphasize understanding of key concepts, effort, and improvement.
Feedback and Improvement: Provide constructive feedback and describe how students can improve through extra help or revising assignments.
Communication: Explain how progress will be communicated to students and parents, including report cards and informal updates.
Special Considerations: Outline accommodations and support available for students with learning differences."""


class TestToolMethods(unittest.TestCase):
    @patch("builtins.open", new_callable=mock_open, read_data=test_prompt)
    @patch("os.path.join", return_value="prompt/syllabus_prompt.txt")
    @patch("os.path.dirname", return_value="")
    def test_ReadTextFile(self, mock_dirname, mock_join, mock_open):
        content = read_text_file("prompt/syllabus_prompt.txt")
        self.assertEqual(content, test_prompt)
        mock_open.assert_called_once_with("prompt/syllabus_prompt.txt", "r")

    def test_SyllabusBuilderInitialization(self):
        syllabus = SyllabusBuilder(subject="Math", grade_level="Grade 4", verbose=True)
        self.assertEqual(syllabus.prompt, test_prompt)
        self.assertEqual(syllabus.model, default_config["model"])
        self.assertEqual(syllabus.grade_level, "grade 4")
        self.assertEqual(syllabus.subject, "Math")
        self.assertEqual(syllabus.customisation, "")
        self.assertTrue(syllabus.verbose)

        syllabus2 = SyllabusBuilder(
            subject="Math",
            grade_level="Grade 4",
            customisation="Focus more on algebra",
            verbose=True,
        )
        self.assertEqual(syllabus2.customisation, "Focus more on algebra")

    def test_CreatePromptTemp(self):
        sb = SyllabusBuilder(grade_level="grade 4", subject="Math")
        prompt = sb.create_prompt_temp()

        self.assertEqual(sb.grade_level_assessments, assessment_prompt)
        self.assertIsInstance(prompt, PromptTemplate)

    @patch("builtins.open", new_callable=mock_open, read_data=custom_test_prompt)
    @patch("os.path.join", return_value="prompt/customisation.txt")
    @patch("os.path.dirname", return_value="")
    def test_create_custom_promptTemp(self, mock_dirname, mock_join, mock_open):
        sb = SyllabusBuilder(
            grade_level="grade 4", subject="Math", customisation="Focus on Geometry"
        )
        prompt = sb.create_custom_promptTemp()

        # Check the template content
        self.assertEqual(prompt.template, custom_test_prompt)

        # Check the input variables
        self.assertEqual(prompt.input_variables, ["customisation", "syllabus"])

        # Check the partial variables format instructions (assuming you have a method get_format_instructions)
        self.assertIn("format_instructions", prompt.partial_variables)
        self.assertIsInstance(prompt, PromptTemplate)

    def test_validate_response_valid(self):
        # Create a valid response dictionary
        valid_response = {
            "title": "Sample Syllabus Title",
            "overview": "Sample overview of the syllabus content.",
            "objectives": [
                "Define the key terms associated with...",
                "Describe the cardiac cycle...",
            ],
            "policies_and_exceptions": {
                "attendance_requirements": "Sample attendance requirements...",
                "make_up_work": "Sample make-up work policy...",
            },
            "grade_level_assessments": {
                "assessment_components": {
                    "assignments": 20,
                    "exams": 25,
                    "projects": 25,
                    "presentations": 15,
                    "participation": 15,
                },
                "grade_scale": {
                    "A": "90-100%",
                    "B": "80-89%",
                    "C": "70-79%",
                    "D": "60-69%",
                    "F": "Below 60%",
                },
            },
            "additional_information": {
                "Visual aids": ["Diagram of the cardiovascular system", ...],
                "Resources": [
                    "Textbook: Electrocardiography for Healthcare Professionals",
                    ...,
                ],
            },
        }

        # Create an instance of SyllabusBuilder
        syllabus_builder = SyllabusBuilder(
            subject="Mathematics", grade_level="Grade 5", verbose=True
        )

        # Call the validate_response method
        is_valid = syllabus_builder.validate_response(valid_response)

        # Assert that the response is valid
        self.assertTrue(is_valid)

    def test_validate_response_invalid(self):
        # Create an invalid response dictionary (missing objectives)
        invalid_response = {
            "title": "Sample Syllabus Title",
            "overview": "Sample overview of the syllabus content.",
            # Missing "objectives"
            "policies_and_exceptions": {
                "attendance_requirements": "Sample attendance requirements...",
                "make_up_work": "Sample make-up work policy...",
            },
            "grade_level_assessments": {
                "assessment_components": {
                    "assignments": 20,
                    "exams": 25,
                    "projects": 25,
                    "presentations": 15,
                    "participation": 15,
                },
                "grade_scale": {
                    "A": "90-100%",
                    "B": "80-89%",
                    "C": "70-79%",
                    "D": "60-69%",
                    "F": "Below 60%",
                },
            },
            "additional_information": {
                "Visual aids": ["Diagram of the cardiovascular system", ...],
                "Resources": [
                    "Textbook: Electrocardiography for Healthcare Professionals",
                    ...,
                ],
            },
        }

        # Create an instance of SyllabusBuilder
        syllabus_builder = SyllabusBuilder(
            subject="Mathematics", grade_level="Grade 5", verbose=True
        )

        # Call the validate_response method
        is_valid = syllabus_builder.validate_response(invalid_response)

        # Assert that the response is invalid
        self.assertFalse(is_valid)

    @patch.object(SyllabusBuilder, "create_custom_promptTemp")
    @patch.object(SyllabusBuilder, "create_prompt_temp")
    @patch("langchain_core.prompts.PromptTemplate", autospec=True)
    @patch("langchain_google_genai.GoogleGenerativeAI", autospec=True)
    @patch("langchain_core.output_parsers.JsonOutputParser", autospec=True)
    def test_compile_customisation_and_syllabus(
        self,
        mock_json_parser,
        mock_google_model,
        mock_prompt_template,
        mock_create_prompt_temp,
        mock_create_custom_promptTemp,
    ):
        mock_custom_prompt_instance = MagicMock(spec=PromptTemplate)
        mock_create_custom_promptTemp.return_value = mock_custom_prompt_instance

        mock_syllabus_prompt_instance = MagicMock(spec=PromptTemplate)
        mock_create_prompt_temp.return_value = mock_syllabus_prompt_instance

        sb = SyllabusBuilder(subject="Mathematics", grade_level="Grade 5", verbose=True)
        # Call the compile method with type "customisation"
        chain_customisation = sb.compile("customisation")

        # Verify that create_custom_promptTemp was called
        mock_create_custom_promptTemp.assert_called_once()

        chain_syllabus = sb.compile("syllabus")
        mock_create_prompt_temp.assert_called_once()

    def test_valid_model(self):
        # Example of a valid input dictionary
        valid_input = {
            "title": "Sample Syllabus Title",
            "overview": "Sample overview of the syllabus content.",
            "objectives": [
                "Define the key terms associated with...",
                "Describe the cardiac cycle...",
            ],
            "policies_and_exceptions": {
                "attendance_requirements": "Sample attendance requirements...",
                "make_up_work": "Sample make-up work policy...",
            },
            "grade_level_assessments": {
                "assessment_components": {
                    "assignments": 20,
                    "exams": 25,
                    "projects": 25,
                    "presentations": 15,
                    "participation": 15,
                },
                "grade_scale": {
                    "A": "90-100%",
                    "B": "80-89%",
                    "C": "70-79%",
                    "D": "60-69%",
                    "F": "Below 60%",
                },
            },
            "additional_information": {
                "Visual aids": ["Diagram of the cardiovascular system", ...],
                "Resources": [
                    "Textbook: Electrocardiography for Healthcare Professionals",
                    ...,
                ],
            },
        }

        # Create an instance of the model with the valid input
        model_instance = SyllabusModel(**valid_input)

        # Assert that the model instance is valid (should not raise ValidationError)
        self.assertEqual(model_instance.title, "Sample Syllabus Title")
        self.assertEqual(model_instance.objectives, valid_input["objectives"])
        # Add more assertions for other fields as needed

    def test_invalid_model(self):
        # Example of an invalid input dictionary (missing required fields)
        invalid_input = {
            "title": "Sample Syllabus Title",
            # Missing "overview", "objectives", "policies_and_exceptions", "grade_level_assessments", "additional_information"
        }

        # Try to create an instance of the model with the invalid input
        with self.assertRaises(ValidationError):
            SyllabusModel(**invalid_input)


if __name__ == "__main__":
    unittest.main()
