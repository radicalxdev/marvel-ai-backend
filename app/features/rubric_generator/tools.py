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
from pylatex import Document, Section, Command, NoEscape, Tabular, MultiColumn
from pylatex import Tabular, Tabularx, LongTable
from pylatex.utils import italic, NoEscape, bold

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
        if int(args.point_scale) < 2 or int(args.point_scale) > 10:
            raise ValueError("Point Scale must be between 2 and 10. Suggested value is 4 for optimal granularity in grading.")
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
    
    def create_pdf_from_rubric(self, rubric_data):
        # Create a LaTeX document
        doc = Document()
        # Add the geometry package with minimum left and right margins
        doc.preamble.append(Command('usepackage', 'geometry'))
        doc.preamble.append(NoEscape(r'\geometry{left=1em,right=1em}'))
        # Add longtable package for multi-page tables
        doc.preamble.append(Command('usepackage', 'longtable'))
        doc.preamble.append(Command('usepackage', 'tabularx'))
        
        doc.preamble.append(Command('title', 'Rubric'))
        doc.preamble.append(Command('author', 'AI Generated'))
        doc.preamble.append(Command('date', NoEscape(r'\today')))

        # Add the title page
        doc.append(NoEscape(r'\maketitle'))

        # Add title and grade level without starting a new page
        doc.append(NoEscape(r'\noindent\textbf{Title:} ' + rubric_data['title'] + r'\\'))
        doc.append(NoEscape(r'\noindent\textbf{Grade Level:} ' + rubric_data['grade_level'] + r'\\'))   

        # Determine the point scale
        num_points = int(self.args.point_scale)

        first_criteria_description = rubric_data['criterias'][0]['criteria_description']
        points = []

        for i in range(num_points):
            # Append each 'points' from the first_criteria_points to the points list
            points.append(first_criteria_description[i]['points']) 

        logger.info(f"points is a list that contains all the points in the point_scale: {points}")
        # Create a table for the rubric
        doc.append(NoEscape(r'\section*{Rubric Criterias}')) 
        
        doc.append(NoEscape(r'\begin{center}'))
        col_definition = 'X' * (num_points + 1)  # +1 for the "Criteria" column
            
        # Create the table with the correct number of columns
        with doc.create(Tabularx(col_definition)) as table:
             # Add table headers
            table.add_hline()
            logger.info(f"header row created")
            header_row = ["Criteria"] + points # Adding point scale as headers
            logger.info(f"header_row: {header_row}")
            table.add_row(header_row)
            table.add_hline()

            # Add rows for each criterion
            for criteria in rubric_data['criterias']:
                # Initialize row with the criterion name
                row = [criteria['criteria']]
                # Append scores for each point description
                for point in range(1, num_points + 1):
                    # Find the corresponding description for this point (if exists)
                    description = next(
                        (desc['description'] for desc in criteria['criteria_description']), 
                                ""
                        )
                    row.append(description)  # Append description or empty string if not found
                table.add_row(row)
                table.add_hline()
        doc.append(NoEscape(r'\end{center}'))  # End the center environment


        # Add feedback section
        doc.append(NoEscape(r'\section*{Feedback/Rubric Evaluation}'))
        doc.append(rubric_data['feedback'] + "\n")

        # Generate the PDF
        pdf_filename = 'generated_rubric'
        doc.generate_pdf(pdf_filename, clean_tex=False)

        # Construct the full path with .pdf extension
        full_path = f"{os.path.abspath(pdf_filename)}.pdf"

        # Check if the file was created successfully
        if not os.path.exists(full_path):
            logger.error(f"Failed to create PDF file: {full_path}")
        else:
            logger.info(f"PDF file created successfully: {full_path}")

        return full_path

    def create_rubric(self, documents: List[Document]):
        logger.info(f"Creating the Rubric")

        chain = self.compile(documents)

         # Log the input parameters
        input_parameters = (
            f"Grade Level: {self.args.grade_level}, "
            f"Point Scale: {self.args.point_scale}, "
            f"Standard: {self.args.standard}, "
            f"Language (YOU MUST RESPOND IN THIS LANGUAGE): {self.args.lang}"
        )
        logger.info(f"Input parameters: {input_parameters}")

        attempt = 0
        max_attempt = 5



        while attempt < max_attempt:
            try:
                response = chain.invoke(input_parameters)
                logger.info(f"Rubric generation response: {response}")
            except Exception as e:
                logger.error(f"Error during rubric generation: {str(e)}")
                attempt += 1
                continue
            if response == None:
                logger.error(f"could not generate Rubric, trying again")
                attempt += 1
                continue

            # Check if "criterias" exist and are valid
            if "criterias" not in response or len(response["criterias"]) == 0:
                logger.error("Rubric generation failed, try again please.")
                attempt += 1
                continue

            if "feedback" not in response:
                logger.error("Rubric generation failed, try again please.")
                attempt += 1
                continue

            # Validate each criterion
            criteria_valid = True
            for criterion in response["criterias"]:
                logger.info(f'criterion: {criterion }')
                logger.info(f'len(criterion["criteria_description"]) : {len(criterion["criteria_description"]) }')
                if "criteria_description" not in criterion or len(criterion["criteria_description"]) != int(self.args.point_scale):
                    logger.info(f'len(criterion["criteria_description"]) : {len(criterion["criteria_description"]) }')
                    logger.error("Mismatch between point scale and criteria description count. Try again please.")
                    criteria_valid = False
                    break  # Exit the for loop if a criterion is invalid
    
            if not criteria_valid:
                attempt += 1
                continue  # Retry the rubric generation if validation failed

            # If everything is valid, break the outer loop
            break

        if attempt >= max_attempt:
            raise ValueError("Error: Unable to generate the Rubric after 5 attempts.")

        if self.verbose: print(f"Deleting vectorstore")
        self.vectorstore.delete_collection()

        return self.create_pdf_from_rubric(response)
        


class CriteriaDescription(BaseModel):
    points: str = Field(..., description="The total points gained by the student according to the point_scale an the level name")
    description: List[str] = Field(..., description="Description for the specific point on the scale")

class RubricCriteria(BaseModel):
    criteria: str = Field(..., description="name of the criteria in the rubric")
    criteria_description: List[CriteriaDescription] = Field(..., description="Descriptions for each point on the scale")
    
class RubricOutput(BaseModel):
    title: str = Field(..., description="the rubric title of the assignment based on the standard input parameter")
    grade_level: str = Field(..., description="The grade level for which the rubric is created")
    criterias: List[RubricCriteria] = Field(..., description="The grading criteria for the rubric")
    feedback: str = Field(..., description="the feedback provided by the AI model on the generated rubric")
    
