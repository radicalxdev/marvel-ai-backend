from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain_core.output_parsers import JsonOutputParser
from langchain_google_genai import GoogleGenerativeAI
from app.services.logger import setup_logger
import os
from typing import List, Optional

logger = setup_logger(__name__)

def read_text_file(file_path: str) -> str:
    """Read the content of a text file."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    absolute_file_path = os.path.join(script_dir, file_path)
    with open(absolute_file_path, "r") as file:
        return file.read()

class SyllabusBuilder:
    def __init__(
        self,
        subject: str,
        grade_level: str,
        course_overview: str = "",
        course_objectives: str = "",
        prompt: str = "",
        model=None,
        parser=None,
        verbose: bool = False,
    ):
        """Initialize SyllabusBuilder with default configurations."""
        default_config = {
            "model": GoogleGenerativeAI(model="gemini-1.0-pro"),
            "parser": JsonOutputParser(),
            "prompt": read_text_file("prompt/Description_prompt.txt"),
        }

        self.prompt = prompt or default_config["prompt"]
        self.model = model or default_config["model"]
        self.parser = parser or default_config["parser"]

        self.subject = subject
        self.grade_level = grade_level
        self.course_overview = course_overview
        self.course_objectives = course_objectives
        self.verbose = verbose

        self._validate_inputs()

    def _validate_inputs(self):
        """Validate inputs to ensure all required fields are provided."""
        if not self.subject:
            raise ValueError("Subject must be provided")
        if not self.grade_level:
            raise ValueError("Grade level must be provided")
        if not self.course_overview:
            raise ValueError("Course overview must be provided")
        if not self.course_objectives:
            raise ValueError("Course objectives must be provided")

    def compile(self) -> RunnableParallel:
        """Compile the prompt and return the runnable chain."""
        prompt = PromptTemplate(
            template=self.prompt,
            input_variables=["subject", "grade_level", "course_overview", "course_objectives"],
            partial_variables={"format_instructions": self.parser.get_format_instructions()},
        )

        chain = prompt | self.model | self.parser

        if self.verbose:
            logger.info("Chain compilation complete")

        return chain

    def create_syllabus(self) -> dict:
        """Create syllabus by invoking the compiled chain."""
        if self.verbose:
            logger.info(
                f"Creating syllabus. Subject: {self.subject}, Grade: {self.grade_level}, Course Overview: {self.course_overview}, Course Objectives: {self.course_objectives}"
            )

        chain = self.compile()

        
        response = chain.invoke(
                {
                    "subject": self.subject,
                    "grade_level": self.grade_level,
                    "course_overview": self.course_overview,
                    "course_objectives": self.course_objectives,
                }
            )
        return response

