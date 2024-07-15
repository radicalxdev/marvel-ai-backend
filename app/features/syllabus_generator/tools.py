from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain_core.output_parsers import JsonOutputParser
from langchain_google_genai import GoogleGenerativeAI
from app.services.logger import setup_logger
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
            "parser": JsonOutputParser(),
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
        if subject is None:
            raise ValueError("Subject must be provided")
        if grade_level is None:
            raise ValueError("Grade level must be provided")

    #custommises the prompt template based on the grade level provided    
    def create_prompt_temp(self):
        if "k" in self.grade_level.lower().strip() :
            self.grade_level_assessments = read_text_file("prompt/elementary.txt")

        elif "grade" in self.grade_level:
           
           if int(self.grade_level.replace("grade ",""))<6:
               self.grade_level_assessments = read_text_file("prompt/primary.txt")

           elif int(self.grade_level.replace("grade ",""))<9:
               self.grade_level_assessments = read_text_file("prompt/middle.txt")

           else:
               self.grade_level_assessments = read_text_file("prompt/highschool.txt")

        else:
            self.grade_level_assessments = read_text_file("prompt/university.txt")

        prompt = PromptTemplate(
            template=self.prompt,
            input_variables=["subject", "grade_level","grade_level_assesments"],
            partial_variables={
                "format_instructions": self.parser.get_format_instructions()
            },
        )
        return prompt
    
    # Returns langchain chain for creating syllabus
    def compile(self):
        
        # retriever = self.vectorstore.as_retriever()
        # runner = RunnableParallel(
        #     {
        #         # "context": retriever,
        #         "subject": RunnablePassthrough(),
        #         "grade_level": RunnablePassthrough(),
        #     }
        # )
        prompt = self.create_prompt_temp()
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
            {"subject": self.subject, "grade_level": self.grade_level, "grade_level_assessments":self.grade_level_assessments}
        )
        return response
