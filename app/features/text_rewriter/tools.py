from langchain_google_genai import GoogleGenerativeAI
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from typing import List, Optional
from langchain_core.documents import Document
from app.services.logger import setup_logger
from langchain_core.prompts import PromptTemplate
from typing import Dict
import os

logger = setup_logger(__name__)


def read_text_file(file_path):
    # Get the directory containing the script file
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Combine the script directory with the relative file path
    absolute_file_path = os.path.join(script_dir, file_path)

    with open(absolute_file_path, 'r') as file:
        return file.read()
    
class TextRewriterPipeline:
    def __init__(self, args, verbose, prompt=None, model=None, parser=None):
        self.verbose = verbose
        self.args = args
        self.model = model or GoogleGenerativeAI(model="gemini-1.5-pro")
        self.parser = parser or JsonOutputParser(pydantic_object=TextRewriterOuput)
        self.prompt = prompt or read_text_file("prompt/text-rewriter-prompt.txt")

    def compile_pipeline(self):
        # Return the chain or pipeline
        prompt = PromptTemplate(
            template=self.prompt,
            input_variables=["instructions", "context"],
            partial_variables={"format_instructions": self.parser.get_format_instructions()}
        )
        pipeline = prompt | self.model | self.parser
        if self.verbose: 
            logger.info(f"Pipeline compiled: {pipeline}")
        return pipeline
    
    def validate_output(self, output:Dict) -> bool:

        try:
            # Assuming the response is already a dictionary
            if isinstance(output, dict):
                if "text_rewriter_output" in output:
                    return True
                else: return False
        except TypeError as e:
            if self.verbose:
                logger.error(f"TypeError during response validation: {e}")
            return False

    def re_writer(self, documents: Optional[List[Document]]):

        pipeline = self.compile_pipeline()
        if documents:
            logger.info("Documents are into the TextRewriterPipeline")
            full_content = [doc.page_content for doc in documents]
            docs = " ".join(full_content)

        inputs = {
            "instructions":self.args.instructions,
            "context": docs if self.args.file_url and self.args.file_type and docs else self.args.text
        }
        
        attempts = 0
        max_attempts = 7 # Allow for more attempts to Rewrite

        # Directly check if the response format is valid
        while attempts < max_attempts:
            output = pipeline.invoke(inputs)
            if self.verbose:
                logger.info(f"Generated response attempt {attempts + 1}: {output}")

            if self.validate_output(output=output):
                if self.verbose and output:
                    logger.info(f"Text Rewritten successfully: {output}")
                break

            if self.verbose: logger.warning(f"Invalid response generated, retrying...")

            # Move to the next attempt regardless of success to ensure progress
            attempts += 1

        # Return the response
        return output

class TextRewriterOuput(BaseModel):
    text_rewriter_output: str = Field(description="This is the re-written text from the llm")