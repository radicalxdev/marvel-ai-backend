from pydantic import BaseModel, Field
from typing import List, Dict
import os
from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_core.output_parsers import JsonOutputParser
from langchain_google_genai import GoogleGenerativeAI
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from app.services.logger import setup_logger

logger = setup_logger(__name__)

def read_text_file(file_path):
    # Get the directory containing the script file
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Combine the script directory with the relative file path
    absolute_file_path = os.path.join(script_dir, file_path)
    
    with open(absolute_file_path, 'r') as file:
        return file.read()
    
class RubricGenerator:
    def __init__(self, args=None, vectorstore_class=Chroma, prompt=None, embedding_model=None, model=None, parser=None, verbose=False):
        default_config = {
            "model": GoogleGenerativeAI(model="gemini-1.5-flash"),
            "embedding_model": GoogleGenerativeAIEmbeddings(model='models/embedding-001'),
            "parser": JsonOutputParser(pydantic_object=RubricOutput),
            "prompt": read_text_file("prompt/rubric-generator-prompt.txt"),
            "vectorstore_class": Chroma
        }

        self.prompt = prompt or default_config["prompt"]
        self.model = model or default_config["model"]
        self.parser = parser or default_config["parser"]
        self.embedding_model = embedding_model or default_config["embedding_model"]

        self.vectorstore_class = vectorstore_class or default_config["vectorstore_class"]
        self.vectorstore, self.retriever, self.runner = None, None, None
        self.args = args
        self.verbose = verbose

        if vectorstore_class is None: raise ValueError("Vectorstore must be provided")
        if args.grade_level is None: raise ValueError("Grade Level must be provided")
        if args.point_scale is None: raise ValueError("Point Scale must be provided")
        if args.standard is None: raise ValueError("Learning Standard must be provided")
        if args.lang is None: raise ValueError("Language must be provided")


    def compile(self, documents: List[Document]):
        # Return the chain
        prompt = PromptTemplate(
            template=self.prompt,
            input_variables=["attribute_collection"],
            partial_variables={"format_instructions": self.parser.get_format_instructions()}
        )

        if self.runner is None:
            logger.info(f"Creating vectorstore from {len(documents)} documents") if self.verbose else None
            self.vectorstore = self.vectorstore_class.from_documents(documents, self.embedding_model)
            logger.info(f"Vectorstore created") if self.verbose else None

            self.retriever = self.vectorstore.as_retriever()
            logger.info(f"Retriever created successfully") if self.verbose else None

            self.runner = RunnableParallel(
                {"context": self.retriever,
                "attribute_collection": RunnablePassthrough()
                }
            )

        chain = self.runner | prompt | self.model | self.parser

        logger.info(f"Chain compilation complete")

        return chain

    def create_rubric(self, documents: List[Document]):
        logger.info(f"Creating the Rubric")

        chain = self.compile(documents)

        response = chain.invoke(f"Grade Level: {self.args.grade_level}, Point Scale: {self.args.point_scale}, Standard: {self.args.standard}, Language (YOU MUST RESPOND IN THIS LANGUAGE): {self.args.lang}")

        if self.verbose: print(f"Deleting vectorstore")
        self.vectorstore.delete_collection()

        return response


class CriteriaDescription(BaseModel):
    point_scale: str = Field(..., description="The point scale for grading")
    description: List[str] = Field(..., description="Description for the specific point on the scale")

class RubricCriteria(BaseModel):
    criteria: str = Field(..., description="name of the criteria in the rubric")
    criteria_description: List[CriteriaDescription] = Field(..., description="Descriptions for each point on the scale")
    
class RubricOutput(BaseModel):
    standard: str = Field(..., description="objective related to the assignment")
    grade_level: str = Field(..., description="The grade level for which the rubric is created")
    criterias: List[RubricCriteria] = Field(..., description="The grading criteria for the rubric")
    
