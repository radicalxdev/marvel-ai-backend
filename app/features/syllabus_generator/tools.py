from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_google_genai import GoogleGenerativeAI
from pydantic import BaseModel, Field, ValidationError
import sys
import os

os.chdir('./app')
sys.path.append(os.getcwd())

from services.logger import setup_logger
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
        customisation:str = "",
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
        self.customisation = customisation

        # self.vectorstore = vectorstore
        self.subject = subject
        self.grade_level = grade_level.lower().strip()
        self.verbose = verbose

        # if vectorstore is None:
        # raise ValueError("Vectorestore must be provided")
        if subject is None or len(subject) <= 2:
            raise ValueError("Subject must be provided")
        if grade_level is None or len(grade_level) == 0:
            raise ValueError("Grade level must be provided")

    #custommises the prompt template based on the grade level provided    
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
    
    def create_custom_promptTemp(self):
        custom_prompt = read_text_file("prompt/customisation.txt")
        prompt = PromptTemplate(
            template=custom_prompt,
            input_variables=["syllabus","customisation"],
            partial_variables={
                "format_instructions": self.parser.get_format_instructions()
            },
        )
        return prompt

    # Returns langchain chain for creating syllabus
    def compile(self,type:str):
        if type=="syllabus":
         prompt = self.create_prompt_temp()
        elif type=="customisation":
            prompt = self.create_custom_promptTemp()

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
        if self.verbose:
            logger.info(
                f"Creating syllabus. Subject: {self.subject}, Grade: {self.grade_level}"
            )

        chain = self.compile("syllabus")
        max_attempts = 3
        response = ""

        response = chain.invoke(
            {
                "subject": self.subject,
                "grade_level": self.grade_level,
                "grade_level_assessments": self.grade_level_assessments
            }
        )
        return response
    
    def apply_customisation(self,syllabus):
        if self.verbose:
            logger.info(
                f"Customising syllabus with {self.customisation}"
            )

        chain = self.compile("customisation")
        max_attempts = 3
        response = ""

        response = chain.invoke(
            {
                "customisation" : self.customisation,
                "syllabus":syllabus
            }
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
    additional_information: object = Field(
        description="Includes any additional requirements inquired by the user. This may include additional resources or additional additional information",
        examples=[{"additional_resources": [ "Campbell Biology", "Essential Cell Biology", "Cell Biology by the Numbers" ],
                   "additional_information": ["This syllabus is designed for 10th-grade students. The language has been simplified and analogies and examples have been added to make the content more accessible."] }]
    )
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
                    },
                    
            },
            "additional_information": {
              "Visual aids":[
                  Diagrams of the cardiovascular system , 
                  Annotated electrocardiogram (ECG) readings , 
                  Videos demonstrating ECG procedures and techniques ,
                  Infographics on the cardiac cycle and conduction system ],
             "Resources":[
               {Textbook: "Electrocardiography for Healthcare Professionals" by Booth and O'Brien},
                Online tutorials and interactive ECG simulations,
                Access to ECG machines and practice materials in the laboratory,
                Recommended articles and research papers on the latest ECG technologies and practices]

            }
            """
        }
    }
