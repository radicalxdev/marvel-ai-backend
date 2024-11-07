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
#from pylatex import Document, Section, Command, NoEscape, Tabular, MultiColumn, Package
#from pylatex import Tabular, Tabularx, LongTable
#from pylatex.utils import italic, NoEscape, bold

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

        self.vectorstore_class = vectorstore_class or default_config["vectorstore_class"]
        self.vectorstore, self.retriever, self.runner = None, None, None
        self.args = args
        self.verbose = verbose

        if vectorstore_class is None: raise ValueError("Vectorstore must be provided")
        if args.orientation is None: raise ValueError("Orientattion must be provided")
        if args.nb_columns is None: raise ValueError("nb_columns must be provided")


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
    
    def create_pdf_from_notes(self, notes_data):
        # Create a LaTeX document
        doc = Document()
        #################################
        # Generate the PDF
        pdf_filename = 'generated_notes'
        try:
            doc.generate_pdf(pdf_filename, clean_tex=False)
        except Exception as e:
            logger.error(f"LaTeX Error: {str(e)}")
            with open(f'{pdf_filename}.log', 'r') as log_file:
                logger.error(log_file.read())

        # Construct the full path with .pdf extension
        full_path = f"{os.path.abspath(pdf_filename)}.pdf"

        # Check if the file was created successfully
        if not os.path.exists(full_path):
            logger.error(f"Failed to create PDF file: {full_path}")
        else:
            logger.info(f"Notes PDF file created successfully: {full_path}")

        return full_path
    
    def validate_notes(self, response: Dict) -> bool:
        ######################
        return True
    
    def create_notes(self, documents: List[Document]):
        logger.info(f"Creating the NOTES")

        chain = self.compile(documents)

         # Log the input parameters
        input_parameters = (
            f"Nb of columns: {self.args.nb_columns}, "
            f"Orientation: {self.args.orientation}"
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

            if self.validate_notes(response) == False:
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

        #return self.create_pdf_from_notes(response)
        return response
        


class KeyConcepts(BaseModel):
    concept: str = Field(..., description="The concept name")
    conceptdescription: List[str] = Field(..., description="Description for the concept")

class MajorKeyConcepts(BaseModel):
    majorconcept: str = Field(..., description="name of the major concept")
    keyconceptdetails: List[KeyConcepts] = Field(..., description="Details for the major concept")
    
class NotesOutput(BaseModel):
    title: str = Field(..., description="title for the notes created based on the uploaded documents")
    summary: str = Field(..., description="A summary containing the main idea and subject discussed in the uploaded documents")
    majorkeyconceptslist: List[MajorKeyConcepts] = Field(..., description="The major key concepts, or the big large title discussed in the uploaded documents")
    
