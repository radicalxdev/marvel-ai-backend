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
    
class NotesGenerator:
    def __init__(self, args=None, vectorstore_class=Chroma, prompt=None, embedding_model=None, model=None, parser=None, verbose=False):
        default_config = {
            "model": GoogleGenerativeAI(model="gemini-1.5-flash"),
            "embedding_model": GoogleGenerativeAIEmbeddings(model='models/embedding-001'),
            "parser": JsonOutputParser(pydantic_object=NotesOutput),
            "prompt": read_text_file("prompt/notes-generator-prompt.txt"),
            "vectorstore_class": Chroma
        }

        self.prompt = prompt or default_config["prompt"]
        self.model = model or default_config["model"]
        self.parser = parser or default_config["parser"]
        self.embedding_model = embedding_model or default_config["embedding_model"]
        self.example = read_text_file("prompt/example.txt")

        self.vectorstore_class = vectorstore_class or default_config["vectorstore_class"]
        self.vectorstore, self.retriever, self.runner = None, None, None
        self.args = args
        self.verbose = verbose

        if vectorstore_class is None: raise ValueError("Vectorstore must be provided")
        if args.orientation is None: raise ValueError("Orientattion must be provided")
        if args.nb_columns is None: raise ValueError("nb_columns must be provided")
        if args.details is None: raise ValueError("details about the notes must be provided")
        if args.topic is None: raise ValueError("topic must be provided")


    def compile(self, documents: List[Document]):
        prompt = PromptTemplate(
            template=self.prompt,
            input_variables=["attribute_collection"],
            partial_variables={"format_instructions": self.parser.get_format_instructions(),
                               "example": self.example 
                               }
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


    def validate_major_concepts(self, response):
        major_concepts_list = response.get("major_key_concepts_list")

        if major_concepts_list is None:
            logger.error("Response does not contain 'major_key_concepts_list' key.")
            return False
        
        major_concepts_count = len(major_concepts_list)
        expected_columns = self.args.nb_columns
        
        if major_concepts_count != expected_columns:
            logger.error(f"Number of major concepts ({major_concepts_count}) does not match the expected number of columns ({expected_columns}).")
            return False
        
        return True
    

    def create_notes(self, documents: List[Document]):
        logger.info(f"Creating the NOTES")

        chain = self.compile(documents)

         # Log the input parameters
        input_parameters = (
            f"Nb of columns: {self.args.nb_columns}, "
            f"Topic: {self.args.topic}, "
            f"Details: {self.args.details}, "
            f"Language: {self.args.lang}"
        )
        logger.info(f"Input parameters: {input_parameters}")
        attempt = 1
        max_attempt = 6

        while attempt < max_attempt:
            try:
                response = chain.invoke(input_parameters)
                logger.info(f"Notes generated during attempt nb: {attempt}")
            except Exception as e:
                logger.error(f"Error during notes generation: {str(e)}")
                attempt += 1
                continue
            if response == None:
                logger.error(f"could not generate Notes, trying again")
                attempt += 1
                continue
            if self.validate_major_concepts(response) == False:
                attempt += 1
                continue

            # If everything is valid, break the outer loop
            break

        if attempt >= max_attempt:
            raise ValueError("Error: Unable to generate Notes after 5 attempts.")
        else:
            logger.info(f"Notes successfully generated after {attempt} attempt(s).")

        if self.verbose: print(f"Deleting vectorstore")
        self.vectorstore.delete_collection()

        return response     
   
        
class KeyConcepts(BaseModel):
    concept: str = Field(..., description="The concept name")
    concept_description: List[str] = Field(..., description="Description for the concept")

class MajorKeyConcepts(BaseModel):
    major_concept: str = Field(..., description="Name of the major concept")
    key_concept_details: List[KeyConcepts] = Field(..., description="Details for the major concept")

class NotesOutput(BaseModel):
    title: str = Field(..., description="Title or main topic for the notes created")
    summary: str = Field(..., description="A summary containing the main idea and subject discussed")
    major_key_concepts_list: List[MajorKeyConcepts] = Field(..., description="The major key concepts, or the big large title discussed")
