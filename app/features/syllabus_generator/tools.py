from typing import List, Tuple, Dict, Any

import os
import json
import time

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field, ValidationError
from langchain_google_genai import GoogleGenerativeAI
from langchain_core.exceptions import OutputParserException


from app.services.logger import setup_logger



logger = setup_logger(__name__)

def read_text_file(file_path):
    # Get the directory containing the script file
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Combine the script directory with the relative file path
    absolute_file_path = os.path.join(script_dir, file_path)
    
    with open(absolute_file_path, 'r') as file:
        return file.read()

class Syllabus:
    def __init__(self, model, attributes, prompt_template, parser, verbose = False):
        self.attributes = attributes
        self.order =['course_title', 'grade_level', 'course_description', 'objectives_topics', 'required_materials', 'num_weeks', 'course_outline', 'grading_policy', 'class_policy', 'customization']
        self.fields_dict = {
            'course_title': 'The title of the course: ',
            'grade_level': 'The grade level of the course: ',
            'course_description': 'The description of the course: ',
            'objectives_topics': 'The topics covered and objectives of the course: ',
            'required_materials': 'The required materials: ',
            'num_weeks': 'The duration of the course in weeks: ',
            'course_outline': 'The outline of the course: ',
            'grading_policy': 'The grading policy: ',
            'class_policy': 'The class policy: ',
            'customization': 'Additional customization notes: '
        }

        self.model = model
        self.prompt_template = prompt_template
        self.parser = parser
        self.verbose = verbose

        self.max_attempts = 5
    
    def compile_context(self):
        context = 'Course Information.\n'
        for ord in self.order:
            entry = self.attributes.get(ord)
            if entry is not None:
                entry = entry.rstrip()
                if entry[-1] != '.':
                    entry += '.'
                context += self.fields_dict[ord] + entry + '\n'
        return context
    
    def validate_response(self) -> bool:
        try:
            # Use Pydantic model to validate the response
            SyllabusFormat(**self.response)
            return True
        except ValidationError as e:
            if self.verbose:
                logger.error(f"Validation error during Syllabus response validation: {e}")
            return False
        except TypeError as e:
            if self.verbose:
                logger.error(f"TypeError during Syllabus response validation: {e}")
            return False
    
    def create_syllabus(self):
        attempts = 0
        syllabus = None
        context = self.compile_context()
        prompt = PromptTemplate(
            template=self.prompt_template,
            input_variables=["context"],
            partial_variables={"format_instructions": self.parser.get_format_instructions()}
        )
        chain = prompt | self.model

        while attempts < self.max_attempts:
            attempts += 1
            response = chain.invoke({"context": context})
            if self.verbose:
                logger.info(f"Generated Syllabus response attempt {attempts}: {response}")
            try:
                self.response = self.parser.parse(response)
                if self.validate_response():
                    return self.response
            except (json.JSONDecodeError, OutputParserException) as e:
                # Log the error or handle it accordingly
                logger.error(f"Error parsing response: {e}")
                    
        # Log if fewer questions are generated
        if syllabus is None:
            logger.warning(f"Syllabus was not created")

        return syllabus
    
class SyllabusBuilder:
    def __init__(self, attributes, model = None, prompt_template = None, parser = None, verbose=False):
        self.verbose = verbose
        self.attributes = attributes

        default_config = {
            "model": GoogleGenerativeAI(model="gemini-1.0-pro", temperature=0.7),
            "prompt_template": read_text_file(r"prompts/syllabus_prompt.txt"),
            "parser": JsonOutputParser(pydantic_object=SyllabusFormat),
        }

        self.model = model or default_config["model"]
        self.prompt_template = prompt_template or default_config["prompt_template"]
        self.parser = parser or default_config["parser"]
    
    def create_syllabus(self):
        syllabus_obj = Syllabus(model = self.model, attributes = self.attributes, prompt_template = self.prompt_template, parser = self.parser, verbose = self.verbose)
        syllabus = syllabus_obj.create_syllabus()
        return syllabus


### We might going to need different pydantic classes for each section 
class SyllabusFormat(BaseModel):
    course_title: str = Field(description = 'title of the course')
    course_description: str = Field(description = 'description of the course')
    objectives_topics: str = Field(description = 'topics covered and objectives of the course')
    required_materials: str = Field(description = 'materials required for the course')
    course_outline: str = Field(description = 'outline of the course')
    grading_policy: str = Field(description = 'graiding policy of the course')
    class_policy: str = Field(description = 'class policy of the course')