from langchain.prompts import PromptTemplate
from langchain_google_genai import GoogleGenerativeAI
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field, validator
from app.services.logger import setup_logger
from app.services.tool_registry import ToolFile
from app.services.logger import setup_logger
import os
from typing import List,Dict

logger = setup_logger(__name__)
relative_path = "features/syllabus_generator"


def read_text_file(file_path):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    absolute_file_path = os.path.join(script_dir, file_path)
    with open(absolute_file_path, 'r') as file:
        return file.read()



class GradingPolicy(BaseModel):
    assignments: int = Field(description="Percentage of grade from assignments")
    quizzes: int = Field(description="Percentage of grade from quizzes")
    exams: int = Field(description="Percentage of grade from exams")
    participation: int = Field(description="Percentage of grade from participation")
    projects: int = Field(description="Percentage of grade from projects")
    other: int = Field(description="Percentage of grade from other components")

class ClassPolicies(BaseModel):
    attendance: str = Field(description="Attendance policy details")
    late_work: str = Field(description="Late work policy details")
    academic_integrity: str = Field(description="Academic integrity policy details")
    participation: str = Field(description="Participation policy details")
    special_considerations: str = Field(description="Special considerations policy details")

class WeeklyTopic(BaseModel):
    week: int = Field(description="Week number")
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
    coursedescription: str = Field(description="Brief overview of the course")
    course_objectives: List[str] = Field(description="List of learning goals and outcomes")
    required_materials: List[str] = Field(description="List of books, tools, or supplies needed")
    grading_policy: GradingPolicy = Field(description="Grading policy details")
    class_policies: ClassPolicies = Field(description="Class policies and exceptions")
    course_outline: CourseOutline = Field(description="Detailed course outline")

    class Config:
        schema_extra = {
            "examples": [
                {
                    "course_title": "Introduction to Biology",
                    "grade_level": "9",
                    "subject": "Biology",
                    "coursedescription": "This course provides an introduction to the fundamental concepts of biology.",
                    "course_objectives": [
                        "Understand the basic principles of cell biology",
                        "Learn about the structure and function of DNA",
                        "Explore the principles of genetics"
                    ],
                    "required_materials": [
                        "Biology textbook by Campbell",
                        "Lab notebook",
                        "Safety goggles"
                    ],
                    "grading_policy": {
                        "assignments": 20,
                        "quizzes": 15,
                        "exams": 40,
                        "participation": 10,
                        "projects": 10,
                        "other": 5
                    },
                    "class_policies": {
                        "attendance": "Students are expected to attend all classes.",
                        "late_work": "Late assignments will be accepted up to one week past the due date.",
                        "academic_integrity": "Plagiarism and cheating are strictly prohibited.",
                        "participation": "Active participation in class discussions is required.",
                        "special_considerations": "If you have any special considerations, please inform the instructor."
                    },
                    "course_outline": {
                        "outline": [
                            {"week": 1, "topic": "Introduction to Biology"},
                            {"week": 2, "topic": "Cell Structure and Function"},
                            {"week": 3, "topic": "DNA and Genetics"},
                            # Add more weeks as needed
                            {"week": 36, "topic": "Final Review and Exam Preparation"}
                        ]
                    }
                }
            ]
        }

class SyllabusGenerator:
    def __init__(self, grade_level, subject, model=None, parser=None, prompt=None):
        feature_config = {
            "model": GoogleGenerativeAI(model="gemini-1.0-pro"),
            "parser": JsonOutputParser(pydantic_object=Syllabus),
            "prompt": read_text_file("prompt/syllabi_gen.txt")
        }
        
        self.prompt = prompt or feature_config["prompt"]
        self.model = model or feature_config["model"]
        self.parser = parser or feature_config["parser"]
        self.grade_level = grade_level
        self.subject = subject

    def compile(self):
        prompt = PromptTemplate(
            template=self.prompt,
            input_variables=["grade_level", "subject"],
            partial_variables={"instructions": self.parser.get_format_instructions()}
        )

        chain = prompt | self.model | self.parser
        logger.debug(chain)

        return chain.invoke({"grade_level": self.grade_level, "subject": self.subject})