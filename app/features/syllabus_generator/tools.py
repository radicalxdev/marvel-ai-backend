import os
from typing import Dict, List

from app.features.syllabus_generator.schema import SyllabusModel
from app.services.logger import setup_logger
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import GoogleGenerativeAI
from pydantic import ValidationError

logger = setup_logger(__name__)


def read_text_file(file_path: str) -> str:
    """Read the content of a text file in the syllabus_generator dir."""
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

        self._validate_inputs(subject, grade_level, options, customisation)

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

        self._post_validate_inputs()

    def _validate_inputs(self, subject, grade_level, options, customisation):
        """Validate inputs to ensure all required fields are provided."""
        if subject is None or len(subject) <= 2 or not isinstance(subject, str):
            raise ValueError("Subject must be provided as a str")
        if (
            grade_level is None
            or len(grade_level) == 0
            or not isinstance(grade_level, str)
        ):
            raise ValueError("Grade level must be provided as a str")
        if options is None or len(options) == 0 or not isinstance(options, list):
            raise ValueError("Options must be provided as a list")
        if customisation is not None and not isinstance(customisation, str):
            raise ValueError("customisation should be str or not specified at all")

    def _post_validate_inputs(self):
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

    def _validate_response(self, response: Dict) -> bool:
        """
        Validates response from LLM
        """
        try:
            SyllabusModel(**response)

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
        for num, option in enumerate(self.options, 2):
            # join the optional commands with "\n" to add to prompt
            if option == "all":
                options_text = "\n".join(
                    [
                        f"{i}: {text}"
                        for i, (_, text) in enumerate(USABLE_OPTIONS.items(), 2)
                    ]
                )
                break
            options_text += f"{num}: {USABLE_OPTIONS[option]}\n"

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
