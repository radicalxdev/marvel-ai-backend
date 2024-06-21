from typing import List, Sequence, Tuple, Dict, Any
from io import BytesIO
from fastapi import UploadFile
from pypdf import PdfReader
from urllib.parse import urlparse
import requests
import os
import json
import time
import docx
from pptx import Presentation
import pandas as pd

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_google_vertexai import VertexAIEmbeddings, VertexAI
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_community.document_loaders import UnstructuredURLLoader
from bs4 import BeautifulSoup
from langchain_community.document_loaders import WebBaseLoader

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
    
def extract_text_from_docx(docx_file):
    doc = docx.Document(docx_file)
    return "\n".join([paragraph.text for paragraph in doc.paragraphs])

def extract_text_from_pptx(pptx_file):
    prs = Presentation(pptx_file)
    text_runs = []
    for slide in prs.slides:
        for shape in slide.shapes:
            if hasattr(shape, "text"):
                text_runs.append(shape.text)
    return "\n".join(text_runs)



class WebPageLoader:
    def __init__(self, web_paths: Sequence[str], verbose=False, **kwargs):
        self.loader = WebBaseLoader(web_paths=web_paths, **kwargs)
        self.verbose = verbose

    def load(self) -> List[Document]:
        documents = []

        for url in self.loader.web_paths:
            try:
                response = requests.get(url)
                response.raise_for_status()  # Raise an error for bad status codes

                # Specify the encoding when parsing HTML content
                soup = BeautifulSoup(response.content, 'lxml', from_encoding=response.encoding)

                # Find all heading tags (h1, h2, h3)
                headings = [heading.get_text().strip() for heading in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])]

                # Find all paragraph tags
                paragraphs = [paragraph.get_text().strip() for paragraph in soup.find_all('p')]

                # Combine headings and paragraphs
                combined_content = "\n".join(headings + paragraphs)

                if combined_content:
                    # Create a Document instance with combined content and metadata
                    metadata = {"source": url}
                    new_doc = Document(page_content=combined_content, metadata=metadata)
                    documents.append(new_doc)

                if self.verbose:
                    if documents:
                        print(f"Successfully loaded content from {url}")
                    else:
                        print(f"No relevant content found at {url}")
            except Exception as e:
                if self.verbose:
                    print(f"Failed to load content from {url}")
                    print(e)

        if not documents and self.verbose:
            print("Unable to load any content from the URLs")

        return documents
    
class UnstructuredLoader:
    def __init__(self, url: str, verbose=False):
        self.url = url
        self.verbose = verbose

    def load(self) -> List[Document]:
        documents = []

        try:
            loader = UnstructuredURLLoader(urls=[self.url])
            loaded_docs = loader.load()
            for doc in loaded_docs:
                # Extract content and metadata
                page_content = doc.page_content
                metadata = {"source": self.url}
                paragraphs = page_content.split('\n')  # Split content into paragraphs
                combined_content = "\n".join([paragraph.strip() for paragraph in paragraphs if paragraph.strip()])

                # Create a Document instance with page content and metadata
                new_doc = Document(page_content=combined_content, metadata=metadata)
                documents.append(new_doc) 
            
            if self.verbose:
                logger.info(f"Successfully loaded content from {self.url}")
        except Exception as e:
            logger.error(f"Failed to load content from {self.url}")
            logger.error(e)

        if not documents:
            raise LoaderError("Unable to load any content from the URL")

        return documents



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

class UploadFileLoader:
    def __init__(self, files: List[UploadFile]):
        self.files = files

    def load(self) -> List[Document]:
        documents = []

        for upload_file in self.files:
            file_type = upload_file.filename.split(".")[-1].lower()
            with upload_file.file as file:
                if file_type == "pdf":
                    pdf_reader = PdfReader(file)
                    for i, page in enumerate(pdf_reader.pages):
                        page_content = page.extract_text()
                        metadata = {"source": upload_file.filename, "page_number": i + 1}

                        doc = Document(page_content=page_content, metadata=metadata)
                        documents.append(doc)

                elif file_type in ["doc", "docx"]:
                    page_content = extract_text_from_docx(file)
                    metadata = {"source": upload_file.filename}
                    doc = Document(page_content=page_content, metadata=metadata)
                    documents.append(doc)

                elif file_type in ["ppt", "pptx"]:
                    page_content = extract_text_from_pptx(file)
                    metadata = {"source": upload_file.filename}
                    doc = Document(page_content=page_content, metadata=metadata)
                    documents.append(doc)

                elif file_type == "csv":
                    df = pd.read_csv(file)
                    page_content = df.to_string()
                    metadata = {"source": upload_file.filename}
                    doc = Document(page_content=page_content, metadata=metadata)
                    documents.append(doc)

                else:
                    raise ValueError(f"Unsupported file type: {file_type}")
                

        return documents

class BytesFileLoader:
    def __init__(self, files: List[Tuple[BytesIO, str]]):
        self.files = files
    
    def load(self) -> List[Document]:
        documents = []
        
        for file, file_type in self.files:
            logger.debug(file_type)
            if file_type.lower() == "pdf":
                pdf_reader = PdfReader(file) #! PyPDF2.PdfReader is deprecated

                for i, page in enumerate(pdf_reader.pages):
                    page_content = page.extract_text()
                    metadata = {"source": file_type, "page_number": i + 1}

                    doc = Document(page_content=page_content, metadata=metadata)
                    documents.append(doc)

            
            elif file_type in ["doc", "docx"]:
                page_content = extract_text_from_docx(file)
                metadata = {"source": file_type}
                doc = Document(page_content=page_content, metadata=metadata)
                documents.append(doc)
                

            elif file_type in ["ppt", "pptx"]:
                page_content = extract_text_from_pptx(file)
                metadata = {"source": file_type}
                doc = Document(page_content=page_content, metadata=metadata)
                documents.append(doc)

            elif file_type == "csv":
                df = pd.read_csv(file)
                page_content = df.to_string()
                metadata = {"source": file_type}
                doc = Document(page_content=page_content, metadata=metadata)
                documents.append(doc)
                    
            else:
                raise ValueError(f"Unsupported file type: {file_type}")
            
        return documents

class LocalFileLoader:
    def __init__(self, file_paths: list[str], expected_file_types=None):
        self.file_paths = file_paths
        self.expected_file_types = expected_file_types or ["pdf"]

    def load(self) -> List[Document]:
        documents = []
        
        # Ensure file paths is a list
        self.file_paths = [self.file_paths] if isinstance(self.file_paths, str) else self.file_paths
    
        for file_path in self.file_paths:
            
            file_type = file_path.split(".")[-1].lower()
            if file_type not in self.expected_file_types:
                raise ValueError(f"Expected file types: {self.expected_file_types}, but got: {file_type}")

            with open(file_path, 'rb') as file:
                if file_type == "pdf":
                    pdf_reader = PdfReader(file)
                    for i, page in enumerate(pdf_reader.pages):
                        page_content = page.extract_text()
                        metadata = {"source": file_path, "page_number": i + 1}

                        doc = Document(page_content=page_content, metadata=metadata)
                        documents.append(doc)

                elif file_type in ["doc", "docx"]:
                    page_content = extract_text_from_docx(file)
                    metadata = {"source": file_path}
                    doc = Document(page_content=page_content, metadata=metadata)
                    documents.append(doc)

                elif file_type in ["ppt", "pptx"]:
                    page_content = extract_text_from_pptx(file)
                    metadata = {"source": file_path}
                    doc = Document(page_content=page_content, metadata=metadata)
                    documents.append(doc)

                elif file_type == "csv":
                    df = pd.read_csv(file)
                    page_content = df.to_string()
                    metadata = {"source": file_path}
                    doc = Document(page_content=page_content, metadata=metadata)
                    documents.append(doc)

                else:
                    raise ValueError(f"Unsupported file type: {file_type}")

                

        return documents

class URLLoader:
    def __init__(self, file_loader=None, expected_file_types=None, verbose=False):
        self.loader = file_loader or BytesFileLoader
        self.expected_file_types = expected_file_types or ["pdf", "doc", "docx", "ppt", "pptx", "csv"]
        self.verbose = verbose

    def load(self, tool_files: List[ToolFile]) -> List[Document]:
        queued_files = []
        documents = []
        any_success = False

        for tool_file in tool_files:
            try:
                url = tool_file.url
                response = requests.get(url)
                parsed_url = urlparse(url)
                path = parsed_url.path
                if parsed_url.netloc in ['.pdf', '.doc', '.docx', '.ppt', '.pptx', '.csv']:                    
                    if response.status_code == 200:
                        file_content = BytesIO(response.content)
                        file_type = tool_file.filename.split(".")[-1].lower()
                        if file_type not in self.expected_file_types:
                            raise LoaderError(f"Expected file types: {self.expected_file_types}, but got: {file_type}")
                        queued_files.append((file_content, file_type))
                        if self.verbose:
                            logger.info(f"Successfully loaded file from {url}")
                        any_success = True
                    else:
                        logger.error(f"Request failed to load file from {url} and got status code {response.status_code}")

                elif parsed_url.netloc in ["youtu.be","m.youtube.com","youtube.com","www.youtube.com","www.youtube-nocookie.com","vid.plus"]:
                    print("Youtube")

                else:
                    # Handle web page loading
                    # web_page_loader = WebPageLoader([url], self.verbose)
                    web_page_loader = UnstructuredLoader(url, self.verbose)
                    web_documents = web_page_loader.load()
                    documents.extend(web_documents)
                    any_success = True
            except Exception as e:
                logger.error(f"Failed to load file from {url}")
                logger.error(e)
                continue


        if any_success and queued_files:
            file_loader = self.loader(queued_files)
            documents = file_loader.load()

            if self.verbose:
                logger.info(f"Loaded {len(documents)} documents")

        if not any_success:
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
        max_attempts = num_questions * 5  # Allow for more attempts to generate questions

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
