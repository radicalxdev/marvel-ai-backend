from pydantic import BaseModel, Field
from typing import List, Dict
import os
from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_google_genai import GoogleGenerativeAI

from app.services.logger import setup_logger

logger = setup_logger(__name__)

def read_text_file(file_path):
    # Get the directory containing the script file
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Combine the script directory with the relative file path
    absolute_file_path = os.path.join(script_dir, file_path)
    
    with open(absolute_file_path, 'r') as file:
        return file.read()
    
class TextRewriter:
    def __init__(self, instructions, prompt=None, model=None, parser=None, verbose=False):
        default_config = {
            "model": GoogleGenerativeAI(model="gemini-1.5-flash"),
            "parser": JsonOutputParser(pydantic_object=RewrittenOutput),
            "prompt": read_text_file("prompt/text-rewriter-prompt.txt"),
        }

        self.prompt = prompt or default_config["prompt"]
        self.model = model or default_config["model"]
        self.parser = parser or default_config["parser"]

        self.instructions = instructions
        self.verbose = verbose
    
    def compile(self):
        # Return the chain
        prompt = PromptTemplate(
            template=self.prompt,
            input_variables=["instructions", "context"],
            partial_variables={"format_instructions": self.parser.get_format_instructions()}
        )

        chain = prompt | self.model | self.parser

        return chain
    
    def validate_output(self, response: Dict) -> bool:
        # TODO: implement a response validator here
        # might need to add more checks
        if 'rewritten_text' in response:
            return True
        return False

    def rewrite(self, documents: List[Document]):
        chain = self.compile()
        doc_content = "\n".join([doc.page_content for doc in documents])

        attempts = 0
        max_attempts = 5

        while attempts < max_attempts:
            response = chain.invoke(
                instructions=self.instructions,
                context=doc_content
            )

            if self.verbose:
                logger.info(f"Generated response attempt {attempts + 1}: {response}")

            # validate response
            if self.validate_output(response):
                break
    
            # if response is invalid, retry
            attempts += 1
        return response
    
class RewrittenOutput(BaseModel):
    rewritten_text: str = Field(description="The rewritten text")