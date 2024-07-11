from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from app.features.quizzify.tools import read_text_file
from langchain_core.output_parsers import JsonOutputParser
from langchain_google_genai import GoogleGenerativeAI
from app.services.logger import setup_logger

logger = setup_logger(__name__)


class SyllabusBuilder:
    def __init__(
        self,
        vectorestore,
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

        self.vectorestore = vectorestore
        self.subject = subject
        self.grade_level = grade_level
        self.verbose = verbose

        if vectorestore is None:
            raise ValueError("Vectorestore must be provided")
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

        retriever = self.vectorestore.as_retriever()
        runner = RunnableParallel(
            {
                "context": retriever,
                "subject": RunnablePassthrough(),
                "grade_level": RunnablePassthrough(),
            }
        )

        chain = runner | prompt | self.model | self.parser

        if self.verbose:
            logger.info("Chain compilation complete")

        return chain

    def create_syllabus(self):
        if self.verbose:
            logger.info(
                f"Creating syllabus. Subject: {self.subject}, Grade: {self.grade_level}"
            )

        chain = self.compile()

        response = chain.invoke(self.subject, self.grade_level)
        return response
