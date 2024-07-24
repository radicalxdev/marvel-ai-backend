import os
import sys
import unittest
from unittest import mock
from unittest.mock import patch, mock_open, MagicMock
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_google_genai import GoogleGenerativeAI
from pydantic import BaseModel, Field, ValidationError
sys.path.insert(0,'/Users/ashadi/kai-ai-backend_7.7.1')

from app.services.logger import setup_logger
from typing import List, Dict
import os

#should be removed later
sys.path.insert(0,'/Users/ashadi/kai-ai-backend_7.7.1/app/features/syllabus_generator')
from tools import SyllabusBuilder
from tools import read_text_file

default_config = {
            "model": GoogleGenerativeAI(model="gemini-1.0-pro")
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
        self.assertEqual(content,test_prompt)
        mock_open.assert_called_once_with("prompt/syllabus_prompt.txt", "r")

    def test_SyllabusBuilderInitialization(self):
        syllabus = SyllabusBuilder(subject="Math", grade_level="Grade 4", verbose=True)
        self.assertEqual(syllabus.prompt,test_prompt)
        self.assertEqual(syllabus.model,default_config["model"])
        self.assertEqual(syllabus.grade_level,"grade 4")
        self.assertEqual(syllabus.subject,"Math")
        self.assertEqual(syllabus.customisation,"")
        self.assertTrue(syllabus.verbose)

        syllabus2 = SyllabusBuilder(subject="Math", grade_level="Grade 4", customisation="Focus more on algebra",verbose=True)
        self.assertEqual(syllabus2.customisation,"Focus more on algebra")

    def test_CreatePromptTemp(self):
        sb = SyllabusBuilder(grade_level="grade 4",subject="Math")
        prompt = sb.create_prompt_temp()

        self.assertEqual(sb.grade_level_assessments,assessment_prompt)
        self.assertIsInstance(prompt,PromptTemplate)


    

if __name__ == "__main__":
    unittest.main()