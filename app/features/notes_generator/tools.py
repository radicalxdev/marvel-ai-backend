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
from reportlab.lib.pagesizes import LETTER, landscape, portrait
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
import roman  # For Roman numeral conversion

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

    def create_pdf_from_notes(self, notes_data):
        # Set up PDF document orientation and filename
        orientation = self.args.orientation
        pdf_filename = "generated_notes.pdf"
        pagesize = landscape(LETTER) if orientation.lower() == "landscape" else portrait(LETTER)
        logger.info(f"create PDF file from the notes, orientation =  {orientation}")
        # Create document
        doc = SimpleDocTemplate(pdf_filename, pagesize=pagesize, rightMargin=0.5*inch, leftMargin=0.5*inch)
        styles = getSampleStyleSheet()

        # Custom styles
        title_style = ParagraphStyle(
            "TitleStyle", parent=styles["Title"], fontSize=16, alignment=1, spaceAfter=12
        )
        concept_style = ParagraphStyle(
            "ConceptStyle", parent=styles["Normal"], leftIndent=24, spaceAfter=6
        )

        # Build PDF content
        content = []

        # Title
        content.append(Paragraph(notes_data["title"], title_style))
        content.append(Spacer(1, 0.2 * inch))

        # Summary
        content.append(Paragraph(notes_data["summary"], styles["BodyText"]))
        content.append(Spacer(1, 0.2 * inch))

        # Numbered Major Key Concepts
        for idx, major_concept in enumerate(notes_data["majorkeyconceptslist"], start=1):
            # Display major concept title with numbering
            major_concept_title = f"{idx}. {major_concept['majorconcept']}"
            content.append(Paragraph(major_concept_title, styles["Heading2"]))

            # Numbered sub-key concepts in Roman numerals
            for sub_idx, key_concept in enumerate(major_concept["keyconceptdetails"], start=1):
                sub_concept_title = f"{roman.toRoman(sub_idx)}. {key_concept['concept']}"
                content.append(Paragraph(sub_concept_title, concept_style))

                # Add each description as a paragraph below the concept title
                for description in key_concept["conceptdescription"]:
                    content.append(Paragraph(description, styles["BodyText"]))
                    content.append(Spacer(1, 0.1 * inch))

            # Add a spacer between major concepts
            content.append(Spacer(1, 0.3 * inch))

        # Generate PDF
        try:
            doc.build(content)
        except Exception as e:
            print(f"Error generating PDF: {str(e)}")

        # Return the absolute path to the PDF file
        full_path = os.path.abspath(pdf_filename)
        return full_path
    
    def create_notes(self, documents: List[Document]):
        logger.info(f"Creating the NOTES")

        chain = self.compile(documents)

         # Log the input parameters
        input_parameters = (
            f"Nb of columns: {self.args.nb_columns}, "
            f"Topic: {self.args.topic}, "
            f"Details: {self.args.details}"
        )
        logger.info(f"Input parameters: {input_parameters}")
        attempt = 1
        max_attempt = 6

        while attempt < max_attempt:
            try:
                response = chain.invoke(input_parameters)
            except Exception as e:
                logger.error(f"Error during notes generation: {str(e)}")
                attempt += 1
                continue
            if response == None:
                logger.error(f"could not generate Notes, trying again")
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

        return self.create_pdf_from_notes(response)       
        


class KeyConcepts(BaseModel):
    concept: str = Field(..., description="The concept name")
    conceptdescription: List[str] = Field(..., description="Description for the concept")

class MajorKeyConcepts(BaseModel):
    majorconcept: str = Field(..., description="name of the major concept")
    keyconceptdetails: List[KeyConcepts] = Field(..., description="Details for the major concept")
    
class NotesOutput(BaseModel):
    title: str = Field(..., description="title or main topic for the notes created")
    summary: str = Field(..., description="A summary containing the main idea and subject discussed")
    majorkeyconceptslist: List[MajorKeyConcepts] = Field(..., description="The major key concepts, or the big large title discussed")
    
