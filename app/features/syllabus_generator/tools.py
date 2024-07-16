from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain_core.output_parsers import JsonOutputParser
from langchain_google_genai import GoogleGenerativeAI
from pydantic import BaseModel, Field, ValidationError
from app.services.logger import setup_logger
from typing import List, Dict
import os

logger = setup_logger(__name__)


def read_text_file(file_path):
    # Get the directory containing the script file
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Combine the script directory with the relative file path
    absolute_file_path = os.path.join(script_dir, file_path)

    with open(absolute_file_path, "r") as file:
        return file.read()


class SyllabusBuilder:
    def __init__(
        self,
        # vectorstore,
        subject: str,
        grade_level: str,
        prompt: str = "",
        model=None,
        parser=None,
        verbose=False,
    ):
        default_config = {
            "model": GoogleGenerativeAI(model="gemini-1.0-pro"),
            "parser": JsonOutputParser(pydantic_object=SyllabusModel),
            "prompt": read_text_file("prompt/syllabus_prompt.txt"),
        }

        self.prompt = prompt or default_config["prompt"]
        self.model = model or default_config["model"]
        self.parser = parser or default_config["parser"]
        self.grade_level_assessments = ""

        # self.vectorstore = vectorstore
        self.subject = subject
        self.grade_level = grade_level
        self.verbose = verbose

        # if vectorstore is None:
        # raise ValueError("Vectorestore must be provided")
        if subject is None or len(subject) <= 2:
            raise ValueError("Subject must be provided")
        if grade_level is None or len(grade_level) == 0:
            raise ValueError("Grade level must be provided")

    # custommises the prompt template based on the grade level provided
    def create_prompt_temp(self):
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
            input_variables=["subject", "grade_level", "grade_level_assesments"],
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

    def validate_response(self, response: Dict) -> bool:
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
                    if isinstance(objectives, dict):
                        for key, value in objectives.items():
                            if isinstance(key, int) or isinstance(value, str):
                                return False
                            objectives_flag = True

                    # Check policies_and_exceptions in correct format
                    policies_and_exceptions = response["policies_and_exceptions"]
                    if isinstance(policies_and_exceptions, list):
                        for item in policies_and_exceptions:
                            if not isinstance(item, str):
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
        if self.verbose:
            logger.info(
                f"Creating syllabus. Subject: {self.subject}, Grade: {self.grade_level}"
            )

        chain = self.compile()
        max_attempts = 3
        response = ""

        for attempt in range(max_attempts):
            response = chain.invoke(
                {
                    "subject": self.subject,
                    "grade_level": self.grade_level,
                    "grade_level_assessments": self.grade_level_assessments,
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
    objectives: Dict[int, str] = Field(
        description="A numbered list of of specific taskts the student will be able to successfully do upon completion of the course",
        examples=[
            {
                1: "Define the key terms associated with electrocardiographs.",
                2: "Describe the cardiac cycle and the conduction systems that controls the cardiac cycle.",
                3: "Describe the electrocardiogram.",
            },
            {
                1: "Craft short plays with clear action, developed characters, and precise dialogue",
                2: "Apply feedback to your own writing through revision",
                3: "Analyse and discuss the craft of contemporary plays",
            },
        ],
    )
    policies_and_exceptions: List[str] = Field(
        description="Class policies, exceptions, important rules and any special consideration all students must be aware of"
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
            "objectives":
                {
                1: "Define the key terms associated with electrocardiographs.",
                2: "Describe the cardiac cycle and the conduction systems that controls the cardiac cycle.",
                3: "Describe the electrocardiogram.",
                4: "Maintain equipment for safety and accuracy; identify and eliminate or report interference and
                    mechanical problems."
                },
                policies_and_exceptions: [
                    "ATTENDANCE REQUIREMENTS:
                    It is important for the school to be notified when a student is not able to attend class. It is the student’s responsibility to
                    inquire about make-up work for both classroom lectures and laboratory sessions.
                    Tardiness and/or absence from any part of a class/lab will constitute a partial absence. A total of three partial absences
                    will constitute a full absence. ",
                    "MAKE-UP WORK:
                    It is the student’s responsibility to inquire about make-up work for both classroom and laboratory sessions. The
                    instructor will not re-teach material, therefore there is no charge for make-up work. For information regarding make-up
                    work."
                ]
            }
            """
        }
    }
