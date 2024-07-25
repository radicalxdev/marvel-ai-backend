import os
from typing import Dict, List

from app.services.logger import setup_logger
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import GoogleGenerativeAI
from pydantic import BaseModel, Field, ValidationError

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
        prompt: str = "",
        model=None,
        parser=None,
        verbose: bool = False,
    ):
        """Initialize SyllabusBuilder with default configurations."""
        default_config = {
            "model": GoogleGenerativeAI(model="gemini-1.0-pro"),
            "parser": JsonOutputParser(pydantic_object=SyllabusModel),
            "prompt": read_text_file("prompt/syllabus_prompt.txt"),
        }

        self.prompt = prompt or default_config["prompt"]
        self.model = model or default_config["model"]
        self.parser = parser or default_config["parser"]
        self.grade_level_assessments = ""

        self.subject = subject
        self.grade_level = grade_level.lower().strip()
        self.course_overview = course_overview
        self.verbose = verbose

        self._validate_inputs()

    def _validate_inputs(self):
        """Validate inputs to ensure all required fields are provided."""
        if self.subject is None or len(self.subject) <= 2:
            raise ValueError("Subject must be provided")
        if self.grade_level is None or len(self.grade_level) == 0:
            raise ValueError("Grade level must be provided")

    # custommises the prompt template based on the grade level provided
    def create_prompt_temp(self) -> PromptTemplate:
        if "k" in self.grade_level.lower().strip():
            self.grade_level_assessments = read_text_file("prompt/elementary.txt")

        elif "grade" in self.grade_level:
            if int(self.grade_level.replace("grade ", "")) < 6:
                self.grade_level_assessments = read_text_file("prompt/primary.txt")

            elif int(self.grade_level.replace("grade ", "")) < 9:
                self.grade_level_assessments = read_text_file("prompt/middle.txt")

            else:
                self.grade_level_assessments = read_text_file("prompt/highschool.txt")

        else:
            self.grade_level_assessments = read_text_file("prompt/university.txt")

        prompt = PromptTemplate(
            template=self.prompt,
            input_variables=[
                "subject",
                "grade_level",
                "grade_level_assessments",
                "course_overview",
            ],
            partial_variables={
                "format_instructions": self.parser.get_format_instructions()
            },
        )
        return prompt

    # Returns langchain chain for creating syllabus
    def compile(self):
        prompt = self.create_prompt_temp()
        chain = prompt | self.model | self.parser

        if self.verbose:
            logger.info("Chain compilation complete")

        return chain

    # Probably a better way to do this
    def validate_response(self, response: Dict) -> bool:
        """
        Validates response from LLM
        """
        policies_and_exceptions_flag = False
        objectives_flag = False

        try:
            # Assuming reponse is already a dict
            if isinstance(response, dict):
                if (
                    "title" in response
                    and "overview" in response
                    and "objectives" in response
                    and "policies_and_exceptions" in response
                ):
                    # Check objectives in correct format
                    objectives = response["objectives"]
                    if isinstance(objectives, list):
                        for item in objectives:
                            if not isinstance(item, str):
                                return False
                        objectives_flag = True

                    # Check policies_and_exceptions in correct format
                    policies_and_exceptions = response["policies_and_exceptions"]
                    if isinstance(policies_and_exceptions, dict):
                        for key, value in policies_and_exceptions.items():
                            if not isinstance(key, str) or not isinstance(value, str):
                                return False
                        policies_and_exceptions_flag = True

            if objectives_flag and policies_and_exceptions_flag:
                if self.verbose:
                    logger.info("Response validated successfully")
                return True

            logger.warn("Response failed to validate")
            return False

        except TypeError as e:
            logger.error(f"TypeError during reponse validation: {e}")
            return False
        except ValidationError as e:
            logger.warn(f"ValidationError during response validation: {e}")
            return False

    def create_syllabus(self):
        """Create syllabus by invoking the compiled chain."""
        if self.verbose:
            logger.info(
                f"Creating syllabus. Subject: {self.subject}, Grade: {self.grade_level}, Course Overview: {self.course_overview}"
            )

        chain = self.compile()
        max_attempts = 3
        response = ""

        for attempt in range(1, max_attempts + 1):
            response = chain.invoke(
                {
                    "subject": self.subject,
                    "grade_level": self.grade_level,
                    "grade_level_assessments": self.grade_level_assessments,
                    "course_overview": self.course_overview,
                }
            )
            if self.verbose:
                logger.info(f"Generated reponse for attempt {attempt}")

            if self.validate_response(response):
                if self.verbose:
                    logger.info("Valid response formed")
                return response
            else:
                logger.warn(
                    f"Invalid response format. Attempt {attempt} of {max_attempts}"
                )
        logger.error(
            f"Failed to generate valid response within {max_attempts} attempts"
        )
        return response


class SyllabusModel(BaseModel):
    title: str = Field(description="The title for the whole course")
    overview: str = Field(
        description="A broad overview of what is expected of students and what they will learn"
    )
    objectives: List[str] = Field(
        description="A list of specific tasks the student will be able to successfully do upon completion of the course",
        examples=[
            [
                "Define the key terms associated with electrocardiographs.",
                "Describe the cardiac cycle and the conduction systems that controls the cardiac cycle.",
                "Describe the electrocardiogram.",
            ],
            [
                "Craft short plays with clear action, developed characters, and precise dialogue",
                "Apply feedback to your own writing through revision",
                "Analyse and discuss the craft of contemporary plays",
            ],
        ],
    )
    policies_and_exceptions: Dict[str, str] = Field(
        description="Class policies, exceptions, important rules and any special consideration all students must be aware of. Each has a title and contents.",
        examples=[
            {
                "performance_expectations": {
                    "mastery_of_subject_matter": "Students are expected to demonstrate a mastery of the subject matter covered in the course.",
                    "critical_analysis": "Students are expected to be able to critically analyze scientific information and arguments.",
                    "research_skills": "Students are expected to be able to conduct research and use scientific literature to support their work.",
                    "professional_behavior": "Students are expected to behave in a professional manner at all times.",
                },
                "feedback_and_improvement": {
                    "feedback_process": "Students will receive feedback on their work through written comments, discussion, and peer review.",
                    "options_for_grade_improvement": "Students may have the opportunity to improve their grades by resubmitting assignments or completing additional work.",
                },
                "communication": {
                    "grades_and_feedback": "Grades and feedback will be communicated to students through the online course management system and in person during office hours.",
                    "academic_advising": "Students may also meet with their academic advisor to discuss their grades and progress in the course.",
                },
                "special_considerations": {
                    "accommodations_for_students_with_disabilities": "Students with disabilities who need accommodations should contact the Disability Services office.",
                    "academic_support_resources": "Students may also access a variety of academic support resources, such as tutoring, writing centers, and counseling services.",
                },
            },
        ],
    )

    grade_level_assessments: Dict[str, Dict[str, int | str]] = Field(
        description="assessment components and grade scale for completing the course. Assessment components being a dictionary of components and percentages, grade_scale being a dictionary of grades and percentage ranges",
        examples=[
            {
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
        ],
    )

    # This can be expanded

    model_config = {
        "json_schema_extra": {
            "examples": """
            {
                "title": "ELECTROCARDIOGRAPH TECHNIQUE & APPLICATION",
                "overview": "Acquiring a deeper understanding of the cardiovascular system and how it functions, students
                    practice basic electrocardiograph patient care techniques, applying legal and ethical responsibilities. Students learn the
                    use of medical instrumentation, electrocardiogram theory, identification of and response to mechanical problems,
                    recognition of cardiac rhythm and response to emergency findings.",
                "objectives": [
                        "Define the key terms associated with electrocardiographs.",
                        "Describe the cardiac cycle and the conduction systems that controls the cardiac cycle.",
                        "Describe the electrocardiogram.",
                        "Maintain equipment for safety and accuracy; identify and eliminate or report interference and
                        mechanical problems."
                    ],
                "policies_and_exceptions": {
                    "attendance requirements":
                        "It is important for the school to be notified when a student is not able to attend class. It is the student’s responsibility to
                        inquire about make-up work for both classroom lectures and laboratory sessions.
                        Tardiness and/or absence from any part of a class/lab will constitute a partial absence. A total of three partial absences
                        will constitute a full absence. ",
                    "make-up work":
                        "It is the student’s responsibility to inquire about make-up work for both classroom and laboratory sessions. The
                        instructor will not re-teach material, therefore there is no charge for make-up work. For information regarding make-up
                        work."
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
                    }
            }
            """
        }
    }
