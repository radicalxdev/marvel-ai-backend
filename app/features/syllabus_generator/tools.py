from langchain.prompts import PromptTemplate
from langchain_google_genai import GoogleGenerativeAI
from langchain_core.output_parsers import JsonOutputParser
#from langchain_ollama import ChatOllama
#from langchain_openai import ChatOpenAI
from langchain_core.pydantic_v1 import BaseModel, Field, validator, ValidationError
from app.services.logger import setup_logger
from app.api.error_utilities import InputValidationError, ToolExecutorError
from app.services.logger import setup_logger
from datetime import datetime, timedelta
import os
#import openai
#from google.auth import default, transport
from typing import List,Dict, Optional

logger = setup_logger(__name__)
relative_path = "features/syllabus_generator"


def read_text_file(file_path):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    absolute_file_path = os.path.join(script_dir, file_path)
    with open(absolute_file_path, 'r') as file:
        return file.read()

class SyllabusGenerator:
    def __init__(self, grade_level, subject, num_weeks, start_date,
                 additional_objectives,additional_materials,
                 additional_grading_policy,additional_class_policy,
                 custom_course_outline,
                 model = None,  parser=None, prompt=None):
        
        feature_config = {
            "model": GoogleGenerativeAI(model="gemini-1.5-pro"), # add google_api_key while testing
            "parser": JsonOutputParser(pydantic_object=Syllabus),
            "prompt": read_text_file("prompt/syllabi_gen.txt")
        }
        
        self.prompt = prompt or feature_config["prompt"]
        self.model = model or feature_config["model"]
        self.parser = parser or feature_config["parser"]
        self.grade_level = grade_level
        self.subject = subject
        self.num_weeks = num_weeks
        self.start_date = datetime.strptime(start_date,"%Y-%m-%d") if start_date else ""
        self.additional_objectives = additional_objectives or ""
        self.additional_materials = additional_materials or ""
        self.additional_grading_policy = additional_grading_policy or ""
        self.additional_class_policy = additional_class_policy or ""
        self.custom_course_outline = custom_course_outline or ""


    def compile(self):
        try:
            input_variables = ["grade_level", "subject", "num_weeks"]
            #optional start date
            if self.start_date:
                input_variables.append("start_date")

            partial_variables = {"instructions": self.parser.get_format_instructions()}

            prompt = PromptTemplate(
                template=self.prompt,
                input_variables=input_variables,
                partial_variables=partial_variables
            )
            chain = prompt | self.model | self.parser
            
            logger.debug("Chain created successfully")

            return chain

        except Exception as e:
            logger.error(f"An error occurred during chain building: {e}")
            raise ToolExecutorError(f"An error occurred during chain building: {e}") from e

    def generate(self):
        try:
            
            chain = self.compile()
            # Create input dictionary for the chain
            input_dict = {
                "grade_level": self.grade_level,
                "subject": self.subject,
                "num_weeks": self.num_weeks,
                "start_date": self.start_date,
                "additional_objectives": self.additional_objectives,
                "additional_materials": self.additional_materials,
                "additional_grading_policy": self.additional_grading_policy,
                "additional_class_policy": self.additional_class_policy,
                "custom_course_outline": self.custom_course_outline                
            }
            # Invoke the chain with the input dictionary
            output = chain.invoke(input_dict)            
            return output

        except ValidationError as e:
            logger.error(f"Validation error: {e}")
            raise InputValidationError(f"Validation error: {e}") from e
        except Exception as e:
            logger.error(f"An error occurred during syllabus generation: {e}")
            raise ToolExecutorError(f"An error occurred during syllabus generation: {e}") from e
        
# data structure
class GradingPolicy(BaseModel):
    assignments: int = Field(description="Percentage of grade from assignments")
    quizzes: int = Field(description="Percentage of grade from quizzes")
    exams: int = Field(description="Percentage of grade from exams")
    participation: int = Field(description="Percentage of grade from participation")
    projects: int = Field(description="Percentage of grade from projects")
    other: int = Field(description="Percentage of grade from other components")
    
    @validator('assignments', 'quizzes', 'exams', 'participation', 'projects', 'other')
    def validate_percentage(cls, v):
        if not (0 <= v <= 100):
            raise ValueError("Percentages must be between 0 and 100")
        return v

class ClassPolicies(BaseModel):
    attendance: str = Field(description="Attendance policy details")
    late_work: str = Field(description="Late work policy details")
    academic_integrity: str = Field(description="Academic integrity policy details")
    participation: str = Field(description="Participation policy details")
    special_considerations: str = Field(description="Special considerations policy details")
    

class WeeklyTopic(BaseModel):
    week: int = Field(description="Week number")
    date: str = Field(description="Date of the week")
    topic: str = Field(description="Topic covered in this week")


class CourseOutline(BaseModel):
    outline: List[WeeklyTopic] = Field(description="Week-by-week outline of topics")

    @validator('outline')
    def validate_outline(cls, v):
        weeks = [item.week for item in v]
        if weeks != list(range(1, len(weeks) + 1)):
            raise ValueError("Week numbers must be consecutive starting from 1")
        return v

class Syllabus(BaseModel):
    course_title: str = Field(description="Title of the course")
    grade_level: str = Field(description="Grade level (K-12 or university)")
    subject: str = Field(description="Subject of the course")
    num_weeks: int = Field(desciption="Number of weeks")
    start_date: Optional[str] = Field(description="Start Date of the Semester")
    course_description: str = Field(description="Brief overview of the course")
    course_objectives: List[str] = Field(description="List of learning goals and outcomes")
    additional_objectives:Optional[str] = Field(description="Additional course objectives by the user")
    required_materials: List[str] = Field(description="List of books, study materials, or tools needed")
    additional_materials: Optional[str] = Field(description="Additional required materials by the user")
    grading_policy: GradingPolicy = Field(description="Grading policy details")
    additional_grading_policy:Optional[str] = Field(description= "grading policy by the user")
    class_policies: ClassPolicies = Field(description="Class policies and exceptions")
    additional_class_policy:Optional[str] = Field(description= "class policy by the user")
    course_outline: CourseOutline = Field(description="Detailed course outline")
    custom_course_outline: Optional[str] = Field(description="course outline by the user")

    class Config:
        schema_extra = {
            "examples": [
                {
                    "course_title": "Introduction to Biology",
                    "grade_level": "ninth",
                    "subject": "Biology",
                    "num_weeks":"36",
                    "start_date":"2023-01-09",
                    "coursedescription": "This course provides an introduction to the fundamental concepts of biology.",
                    "course_objectives": [
                        "Understand the basic principles of cell biology",
                        "Learn about the structure and function of DNA",
                        "Explore the principles of genetics"
                    ],
                    "additional_objectives":"",
                    "required_materials": [
                        "Biology textbook by Campbell",
                        "Book:On the Origin of Species by Charles Darwin"
                        "https://www.khanacademy.org/science/ms-biology/x0c5bb03129646fd6:cells-and-organisms",
                        "Lab notebook"
                    ],
                    "additional_materials":"",
                    "grading_policy": {
                        "assignments": 20,
                        "quizzes": 15,
                        "exams": 40,
                        "participation": 10,
                        "projects": 10,
                        "other": 5   
                    },
                    "additional_grading_policy":"",
                    "class_policies": {
                        "attendance": "Students are expected to attend all classes.",
                        "late_work": "Late assignments will be accepted up to one week past the due date.",
                        "academic_integrity": "Plagiarism and cheating are strictly prohibited.",
                        "participation": "Active participation in class discussions is required.",
                        "special_considerations": "Extra credit available for special projects."
                        
                    },
                    "additional_class_policy":"",
                    "course_outline": {
                        "outline": [
                            {"week": 1, "date": "2023-01-09", "topic": "Introduction to Biology" },
                            {"week": 2, "date": "2023-01-16", "topic": "Cell Structure and Function"},
                            {"week": 3, "date": "2023-01-23", "topic": "DNA and Genetics"},
                            # Add more weeks as needed
                            {"week": 36, "date": "2023-09-18", "topic": "Final Review and Exam Preparation"}
                        ]
                    },
                    "custom_course_outline":""
                }
            ]
        }
        