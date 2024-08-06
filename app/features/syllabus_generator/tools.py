import os
import sys
from typing import Dict, List, Optional

from app.features.syllabus_generator.model import SyllabusModel
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


ALLOWED_OPTIONS = {
    "all": None,
    "title": "Include a title for the syllabus.",
    "overview": "Generate a comprehensive overview of the course.",
    "objectives": "Generate a list of learning objectives to show a student's understanding.",
    "required_materials": "Generate a list of materials that are required by the students to successfully participate in the course. Materials could be things like books, tools or supplies. Use two key variables in the output of required_materials. One is recommended_books and another is required_items.",
    "additional_information": "Include any additional information that could be useful to the student",
    "policies_and_exceptions": "Create a dictionary of policies and exceptions that apply to the course.",
    "grade_level_assessments": "{grade_level_assessments}",
}

# Options that can be added to prompt
USABLE_OPTIONS = ALLOWED_OPTIONS.copy()
USABLE_OPTIONS.pop("all", None)


class SyllabusBuilder:
    def __init__(
        self,
        subject: str,
        grade_level: str,
        course_overview: str = "",
        customisation: str = "",
        options: List[str] = ["all"],
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
        self.customisation = customisation
        self.options = list(map(lambda x: x.strip().lower(), options))

        self.subject = subject
        self.grade_level = grade_level.strip().lower()
        self.course_overview = course_overview
        self.verbose = verbose

        self._validate_inputs()

    def _validate_inputs(self):
        """Validate inputs to ensure all required fields are provided."""
        if self.subject is None or len(self.subject) <= 2:
            raise ValueError("Subject must be provided")
        if self.grade_level is None or len(self.grade_level) == 0:
            raise ValueError("Grade level must be provided")
        if self.options is None or len(self.options) == 0:
            raise ValueError("Options must be provided")

        # Guarantee options only contains "all" or doesn't contain it at all
        seen_all = False
        for item in self.options:
            if seen_all:
                raise ValueError(
                    "Invalid options provided: 'all' option already specified"
                )
            if item not in ALLOWED_OPTIONS:
                raise ValueError("Invalid options provided")
            if item == "all":
                seen_all = True

    # Probably a better way to do this
    # TODO: UPDATE THIS
    def _validate_response(self, response: Dict) -> bool:
        """
        Validates response from LLM
        """
        try:
            # Assuming reponse is already a dict
            if isinstance(response, dict):
                if (
                    "title" in response
                    and "overview" in response
                    and "objectives" in response
                    and "policies_and_exceptions" in response
                    and "required_materials" in response
                ):
                    # Check objectives in correct format
                    objectives = response["objectives"]
                    if isinstance(objectives, list):
                        for item in objectives:
                            if not isinstance(item, str):
                                return False

                    # Check policies_and_exceptions in correct format
                    policies_and_exceptions = response["policies_and_exceptions"]
                    if isinstance(policies_and_exceptions, dict):
                        for key, value in policies_and_exceptions.items():
                            if not isinstance(key, str) or not isinstance(value, str):
                                return False

                    # Check required_materials in correct format
                    required_materials = response["required_materials"]
                    if isinstance(required_materials, dict):
                        for key, val in required_materials.items():
                            if not isinstance(key, str) or not isinstance(val, list):
                                return False
                        required_keys = {"recommended_books", "required_items"}
                        if set(required_materials.keys()) != required_keys:
                            return False

            if self.verbose:
                logger.info("Response validated successfully")
            return True

        except TypeError as e:
            logger.error(f"TypeError during reponse validation: {e}")
            return False
        except ValidationError as e:
            logger.warn(f"ValidationError during response validation: {e}")
            return False

    # custommises the prompt template based on the grade level provided
    def _create_prompt_temp(self) -> PromptTemplate:
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

        options_text = ""
        for num, item in enumerate(self.options, 2):
            # join the optional commands with "\n" to add to prompt
            if item == "all":
                options_text = "\n".join(
                    [
                        f"{i}: {text}"
                        for i, (_, text) in enumerate(USABLE_OPTIONS.items(), 2)
                    ]
                )
                break
            options_text += f"{num}: {USABLE_OPTIONS[item]}\n"

        self.prompt = self.prompt.format(options_text=options_text)

        prompt = PromptTemplate(
            template=self.prompt,
            input_variables=[
                "subject",
                "grade_level",
                "grade_level_assessments",
                "course_overview",
                "customisation",
            ],
            partial_variables={
                "format_instructions": self.parser.get_format_instructions()
            },
        )
        return prompt

    def _create_custom_promptTemp(self):
        custom_prompt = read_text_file("prompt/customisation.txt")
        prompt = PromptTemplate(
            template=custom_prompt,
            input_variables=["syllabus", "customisation"],
            partial_variables={
                "format_instructions": self.parser.get_format_instructions()
            },
        )
        return prompt

    # Returns langchain chain for creating syllabus
    def _compile(self, case: str):
        if case == "syllabus":
            prompt = self._create_prompt_temp()
        elif case == "customisation":
            prompt = self._create_custom_promptTemp()
        else:
            raise ValueError(f"Invalid compile type: {case}")

        chain = prompt | self.model | self.parser

        if self.verbose:
            logger.info("Chain compilation complete")

        return chain

    def create_syllabus(self):
        """Create syllabus by invoking the compiled chain."""
        if self.verbose:
            logger.info(
                f"Creating syllabus. Subject: {self.subject}, Grade: {self.grade_level}, Course Overview: {self.course_overview}"
            )

        chain = self._compile("syllabus")
        max_attempts = 3
        response = ""

        for attempt in range(1, max_attempts + 1):
            response = chain.invoke(
                {
                    "subject": self.subject,
                    "grade_level": self.grade_level,
                    "grade_level_assessments": self.grade_level_assessments,
                    "course_overview": self.course_overview,
                    "customisation": self.customisation,
                }
            )

            if self._validate_response(response):
                if self.verbose:
                    logger.info(f"Generated valid reponse for attempt {attempt}")
                return response
            else:
                logger.warn(
                    f"Invalid response format. Attempt {attempt} of {max_attempts}"
                )
            logger.error(
                f"Failed to generate valid response within {max_attempts} attempts"
            )
        # return anyway cause you probably want to see it anyway
        return response

    def _apply_customisation(self, syllabus):
        if self.verbose:
            logger.info(f"Customising syllabus with {self.customisation}")

        chain = self._compile("customisation")
        max_attempts = 3
        response = ""

        response = chain.invoke(
            {"customisation": self.customisation, "syllabus": syllabus}
        )
        for attempt in range(1, max_attempts + 1):
            if self._validate_response(response):
                if self.verbose:
                    logger.info(f"Generated valid reponse for attempt {attempt}")
                return response
            else:
                logger.warn(
                    f"Invalid response format. Attempt {attempt} of {max_attempts}"
                )
            logger.error(
                f"Failed to generate valid response within {max_attempts} attempts"
            )
        # return anyway cause you probably want to see it anyway
        return response
