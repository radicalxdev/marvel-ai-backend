from typing import List, Tuple, Dict, Any
from io import BytesIO
from fastapi import UploadFile
from pypdf import PdfReader
from urllib.parse import urlparse
import requests
import os
import json
import time
import pymupdf
import re
import pandas as pd

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_google_vertexai import VertexAIEmbeddings, VertexAI
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field
from docx import Document as docu


from services.logger import setup_logger
from services.tool_registry import ToolFile
from api.error_utilities import LoaderError

relative_path = "features/quzzify"

logger = setup_logger(__name__)

def read_text_file(file_path):
    # Get the directory containing the script file
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Combine the script directory with the relative file path
    absolute_file_path = os.path.join(script_dir, file_path)
    
    with open(absolute_file_path, 'r') as file:
        return file.read()

class RAGRunnable:
    def __init__(self, func):
        self.func = func
    
    def __or__(self, other):
        def chained_func(*args, **kwargs):
            # Result of previous function is passed as first argument to next function
            return other(self.func(*args, **kwargs))
        return RAGRunnable(chained_func)
    
    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)

class UploadPDFLoader:
    def __init__(self, files: List[UploadFile]):
        self.files = files

    def load(self) -> List[Document]:
        documents = []

        for upload_file in self.files:
            with upload_file.file as pdf_file:
                pdf_reader = PdfReader(pdf_file)

                for i, page in enumerate(pdf_reader.pages):
                    page_content = page.extract_text()
                    metadata = {"source": upload_file.filename, "page_number": i + 1}

                    doc = Document(page_content=page_content, metadata=metadata)
                    documents.append(doc)

        return documents

class BytesFileCSVLoader:

    def __init__(self, files: List[Tuple[BytesIO, str]]):
        self.files = files
    
    def load(self) -> List[Document]:
        documents = []
        
        for file, file_type in self.files:
            logger.debug(file_type)
            if file_type.lower() == "csv":
                logger.info(file)
                # pdf_reader = PdfReader(file) #! PyPDF2.PdfReader is deprecated
                file.seek(0)
                df = pd.read_csv(file)
                for row in df.itertuples():
                    content = ""
                    for column in row[1:]:
                        content+= (str(column).strip() + "\n")
                    metadata = {"page_number": row[0] + 1, "source": file_type}
                    doc = Document(page_content=content, metadata=metadata)
                    documents.append(doc)               
            else:
                raise ValueError(f"Unsupported file type: {file_type}")
            
        return documents

class BytesFileXLSXLoader:

    def __init__(self, files: List[Tuple[BytesIO, str]]):
        self.files = files
    
    def load(self) -> List[Document]:
        documents = []
        
        for file, file_type in self.files:
            logger.debug(file_type)
            if file_type.lower() == "xlsx":
                logger.info(file)
                # pdf_reader = PdfReader(file) #! PyPDF2.PdfReader is deprecated
                file.seek(0)
                df = pd.read_excel(file)
                for row in df.itertuples():
                    content = ""
                    for column in row[1:]:
                        content+= (str(column).strip() + "\n")
                    metadata = {"page_number": row[0] + 1, "source": file_type}
                    doc = Document(page_content=content, metadata=metadata)
                    documents.append(doc)               
            else:
                raise ValueError(f"Unsupported file type: {file_type}")
            
        return documents
     
class DocLoader:

    def __init__(self, files: List[Tuple[BytesIO, str]]):
        self.files = files
    
    def load(self) -> List[Document]:
        documents = []
        
        for file, file_type in self.files:
            logger.debug(file_type)
            if file_type.lower() == "docx":
                logger.info(file)
                # pdf_reader = PdfReader(file) #! PyPDF2.PdfReader is deprecated
                docs = docu(file)
                for page_num, page in enumerate(docs.paragraphs):
                    page_content = ""
                    for paragraph in page.runs:
                        page_content += paragraph.text.strip() + "\n"
                    metadata = {"page_number": page_num + 1, "source": file_type}
                    doc = Document(page_content=page_content.rstrip(),metadata=metadata)
                    documents.append(doc)               
            else:
                raise ValueError(f"Unsupported file type: {file_type}")
            
        return documents
    

class BytesFilePDFLoader:
    # Original def __init__(self, files: List[Tuple[BytesIO, str]])
    def __init__(self, files: List[Tuple[BytesIO, str]]):
        self.files = files
    
    def load(self) -> List[Document]:
        documents = []
        
        for file, file_type in self.files:
            logger.debug(file_type)
            if file_type.lower() == "pdf":
                logger.info(file)
                # pdf_reader = PdfReader(file) #! PyPDF2.PdfReader is deprecated
                pdf_reader = pymupdf.open(stream=file)
                for pages in range(pdf_reader.page_count):
                    page = pdf_reader.load_page(page_id=pages)
                # documents.append(pdf_reader)
                    metadata = {"source" : file_type, "page_number" : pages + 1}
                    doc = Document(page_content=page.get_text(), metadata= metadata)
                    documents.append(doc)

                # for i, page in enumerate(pdf_reader.pages):
                # for page in data:
                    # page_content = page.extract_text()
                    # metadata = {"source": file_type, "page_number": i + 1}

                    # doc = Document(page_content=page_content, metadata=metadata)
                    # documents.append(doc)
                    # documents.append(page)
                    
            else:
                raise ValueError(f"Unsupported file type: {file_type}")
            
        return documents

class LocalFileLoader:
    def __init__(self, file_paths: list[str], file_loader=None):
        self.file_paths = file_paths
        self.expected_file_types = ["xlsx", "pdf", "pptx", "csv", "docx",]
        self.loader = file_loader or BytesFileXLSXLoader or BytesFilePDFLoader or BytesFileCSVLoader or DocLoader

    def load(self) -> List[Document]:
        documents = []
        
        # Ensure file paths is a list
        self.file_paths = [self.file_paths] if isinstance(self.file_paths, str) else self.file_paths
    
        for file_path in self.file_paths:
            
            file_type = file_path.split(".")[-1]

            if file_type not in self.expected_file_types:
                exp_file_type = self.expected_file_types.join(", ")
                raise ValueError(f"Expected file types: {exp_file_type}, but got: {file_type}")

            with open(file_path, 'rb') as file:
                pdf_reader = PdfReader(file)

                for i, page in enumerate(pdf_reader.pages):
                    page_content = page.extract_text()
                    metadata = {"source": file_path, "page_number": i + 1}

                    doc = Document(page_content=page_content, metadata=metadata)
                    documents.append(doc)

        return documents

class URLLoader:
    def __init__(self, verbose=False):
        self.loaders = [BytesFileXLSXLoader,BytesFilePDFLoader,BytesFileCSVLoader,DocLoader]
        self.expected_file_types = ["xlsx", "pdf", "pptx", "csv", "docx",]
        self.verbose = verbose
   
    def download_from_drive(self,file_id : str):
        download_url = "https://docs.google.com/uc?export=download&id=" + file_id

        response = requests.get(download_url, stream=True)

        # Check for confirmation prompt
        if response.status_code == 302:  # Found a redirect, likely confirmation needed
            logger.info("Google Drive requires confirmation to download the file.")
            logger.info("Please visit the provided URL in your browser and allow access.")
            logger.info(response.headers['Location'])  # Print the redirection URL
            return None  # Indicate download not completed
        
        # Download logic (assuming confirmation was successful)
        file_type = ''
        content_disposition = response.headers.get('Content-Disposition')
        if content_disposition:
            filename_part = content_disposition.split('=')[-1]
            if '.' in filename_part:
                file_type = filename_part.split('.')[-1].lower()[:len(filename_part.split('.')[-1]) - 1]

        return (response,file_type)


    def load(self, tool_files: List[ToolFile]) -> List[Document]:
        queued_files = []
        documents = []
        # any_success = False
        response = None

        for tool_file in tool_files:
            try:
                url = tool_file.url

                regex = r"/d/([^?]+)/"
                match = re.search(regex,url)
                if match:
                    file_id = match.group(1)
                    response,file_type = self.download_from_drive(file_id)
                else:
                    response = requests.get(url)
                    parsed_url = urlparse(url)
                    path = parsed_url.path

                if response.status_code == 200:
                    # Read file
                    file_content = BytesIO(response.content)

                    # Check file type
                    # file_type = path.rsplit(".")[-1]
                    if not file_type:
                        file_type = url.rsplit('.')[-1]
                    if file_type not in  self.expected_file_types:
                        string = self.expected_file_types.join(", ")
                        raise LoaderError(f"Expected file type: {string}, but got: {file_type}")

                    # Append to Queue
                    queued_files.append((file_content, file_type))
                    if self.verbose:
                        logger.info(f"Successfully loaded file from {url}")
                    
                else:
                    logger.error(f"Request failed to load file from {url} and got status code {response.status_code}")

            except Exception as e:
                logger.error(f"Failed to load file from {url}")
                logger.error(e)
                continue

        # Pass Queue to the file loader if there are any successful loads
        if len(queued_files) > 0:
            documents = []
            for file in queued_files: # run each file one by one
                for loader in self.loaders: # cycle loaders until correct loader
                    try:
                        file_loader = loader([file])
                        documents.extend(file_loader.load())
                        if self.verbose:
                            logger.info(f"Loaded {len(documents)} documents")
                    except ValueError: # wrong loader, try next
                        pass
            

        else:
            raise LoaderError("Unable to load any files from URLs")

        return documents

class RAGpipeline:
    def __init__(self, loader=None, splitter=None, vectorstore_class=None, embedding_model=None, verbose=False):
        default_config = {
            "loader": URLLoader(verbose = verbose), # Creates instance on call with verbosity
            "splitter": RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100),
            "vectorstore_class": Chroma,
            "embedding_model": VertexAIEmbeddings(model='textembedding-gecko')
        }
        self.loader = loader or default_config["loader"]
        self.splitter = splitter or default_config["splitter"]
        self.vectorstore_class = vectorstore_class or default_config["vectorstore_class"]
        self.embedding_model = embedding_model or default_config["embedding_model"]
        self.verbose = verbose

    def load_PDFs(self, files) -> List[Document]:
        if self.verbose:
            logger.info(f"Loading {len(files)} files")
            logger.info(f"Loader type used: {type(self.loader)}")
        
        logger.debug(f"Loader is a: {type(self.loader)}")
        
        try:
            total_loaded_files = self.loader.load(files)
        except LoaderError as e:
            logger.error(f"Loader experienced error: {e}")
            raise LoaderError(e)
            
        return total_loaded_files
    
    def split_loaded_documents(self, loaded_documents: List[Document]) -> List[Document]:
        if self.verbose:
            logger.info(f"Splitting {len(loaded_documents)} documents")
            logger.info(f"Splitter type used: {type(self.splitter)}")
            
        total_chunks = []
        chunks = self.splitter.split_documents(loaded_documents)
        total_chunks.extend(chunks)
        
        if self.verbose: logger.info(f"Split {len(loaded_documents)} documents into {len(total_chunks)} chunks")
        
        return total_chunks
    
    def create_vectorstore(self, documents: List[Document]):
        if self.verbose:
            logger.info(f"Creating vectorstore from {len(documents)} documents")
        
        self.vectorstore = self.vectorstore_class.from_documents(documents, self.embedding_model)

        if self.verbose: logger.info(f"Vectorstore created")
        return self.vectorstore
    
    def compile(self):
        # Compile the pipeline
        self.load_PDFs = RAGRunnable(self.load_PDFs)
        self.split_loaded_documents = RAGRunnable(self.split_loaded_documents)
        self.create_vectorstore = RAGRunnable(self.create_vectorstore)
        if self.verbose: logger.info(f"Completed pipeline compilation")
    
    def __call__(self, documents):
        # Returns a vectorstore ready for usage 
        
        if self.verbose: 
            logger.info(f"Executing pipeline")
            logger.info(f"Start of Pipeline received: {len(documents)} documents of type {type(documents[0])}")
        
        pipeline = self.load_PDFs | self.split_loaded_documents | self.create_vectorstore
        return pipeline(documents)

class QuizBuilder:
    def __init__(self, vectorstore, topic, prompt=None, model=None, parser=None, verbose=False):
        default_config = {
            "model": VertexAI(model="gemini-1.0-pro"), 
            "parser": JsonOutputParser(pydantic_object=QuizQuestion),
            "prompt": read_text_file("prompt/quizzify-prompt.txt")
        }
        
        self.prompt = prompt or default_config["prompt"]
        self.model = model or default_config["model"]
        self.parser = parser or default_config["parser"]
        
        self.vectorstore = vectorstore
        self.topic = topic
        self.verbose = verbose
        
        if vectorstore is None: raise ValueError("Vectorstore must be provided")
        if topic is None: raise ValueError("Topic must be provided")
    
    def compile(self):
        # Return the chain
        prompt = PromptTemplate(
            template=self.prompt,
            input_variables=["topic"],
            partial_variables={"format_instructions": self.parser.get_format_instructions()}
        )
        
        retriever = self.vectorstore.as_retriever()
        
        runner = RunnableParallel(
            {"context": retriever, "topic": RunnablePassthrough()}
        )
        
        chain = runner | prompt | self.model | self.parser
        
        if self.verbose: logger.info(f"Chain compilation complete")
        
        return chain

    def validate_response(self, response: Dict) -> bool:
        try:
            # Assuming the response is already a dictionary
            if isinstance(response, dict):
                if 'question' in response and 'choices' in response and 'answer' in response and 'explanation' in response:
                    choices = response['choices']
                    if isinstance(choices, dict):
                        for key, value in choices.items():
                            if not isinstance(key, str) or not isinstance(value, str):
                                return False
                        return True
            return False
        except TypeError as e:
            if self.verbose:
                logger.error(f"TypeError during response validation: {e}")
            return False

    def format_choices(self, choices: Dict[str, str]) -> List[Dict[str, str]]:
        return [{"key": k, "value": v} for k, v in choices.items()]
    
    def create_questions(self, num_questions: int = 5) -> List[Dict]:
        if self.verbose: logger.info(f"Creating {num_questions} questions")
        
        if num_questions > 10:
            return {"message": "error", "data": "Number of questions cannot exceed 10"}
        
        chain = self.compile()
        
        generated_questions = []
        attempts = 0
        max_attempts = num_questions * 10  # Allow for more attempts to generate questions

        while len(generated_questions) < num_questions and attempts < max_attempts:
            response = chain.invoke(self.topic)
            if self.verbose:
                logger.info(f"Generated response attempt {attempts + 1}: {response}")
            
            # Directly check if the response format is valid
            if self.validate_response(response):
                response["choices"] = self.format_choices(response["choices"])
                generated_questions.append(response)
                if self.verbose:
                    logger.info(f"Valid question added: {response}")
                    logger.info(f"Total generated questions: {len(generated_questions)}")
            else:
                if self.verbose:
                    logger.warning(f"Invalid response format. Attempt {attempts + 1} of {max_attempts}")
            
            # Move to the next attempt regardless of success to ensure progress
            attempts += 1

        # Log if fewer questions are generated
        if len(generated_questions) < num_questions:
            logger.warning(f"Only generated {len(generated_questions)} out of {num_questions} requested questions")
        
        if self.verbose: logger.info(f"Deleting vectorstore")
        self.vectorstore.delete_collection()
        
        # Return the list of questions
        return generated_questions[:num_questions]

class QuestionChoice(BaseModel):
    key: str = Field(description="A unique identifier for the choice using letters A, B, C, D, etc.")
    value: str = Field(description="The text content of the choice")
class QuizQuestion(BaseModel):
    question: str = Field(description="The question text")
    choices: List[QuestionChoice] = Field(description="A list of choices")
    answer: str = Field(description="The correct answer")
    explanation: str = Field(description="An explanation of why the answer is correct")
