import unittest
from unittest import mock
import sys
from unittest.mock import patch, mock_open, MagicMock
import os
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_google_genai import GoogleGenerativeAI
from pydantic import BaseModel, Field, ValidationError
import sys
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

    

if __name__ == "__main__":
    unittest.main()