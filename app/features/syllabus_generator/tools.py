from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain_core.output_parsers import JsonOutputParser
from langchain_google_genai import GoogleGenerativeAI
from pydantic import BaseModel, Field
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

        # self.vectorstore = vectorstore
        self.subject = subject
        self.grade_level = grade_level
        self.verbose = verbose

        # if vectorstore is None:
        # raise ValueError("Vectorestore must be provided")
        if subject is None:
            raise ValueError("Subject must be provided")
        if grade_level is None:
            raise ValueError("Grade level must be provided")

    # Returns langchain chain for creating syllabus
    def compile(self):
        prompt = PromptTemplate(
            template=self.prompt,
            input_variables=["subject", "grade_level"],
            partial_variables={
                "format_instructions": self.parser.get_format_instructions()
            },
        )

        chain = prompt | self.model | self.parser

        if self.verbose:
            logger.info("Chain compilation complete")

        return chain

    def create_syllabus(self):
        if self.verbose:
            logger.info(
                f"Creating syllabus. Subject: {self.subject}, Grade: {self.grade_level}"
            )

        chain = self.compile()

        response = chain.invoke(
            {"subject": self.subject, "grade_level": self.grade_level}
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
    # resources: List[str] = Field(
    #     description="A list of exisiting resources such as books, websites that can be used to learn key topics for the course"
    # )
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
