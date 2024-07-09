from typing import List, Tuple, Dict, Any
from io import BytesIO
from fastapi import UploadFile
from pypdf import PdfReader
from urllib.parse import urlparse
from PIL import Image
import urllib.request
import requests
import os
import json
import time
import pymupdf
import re
import pandas as pd
import pytesseract

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_google_vertexai import VertexAIEmbeddings, VertexAI
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_core.output_parsers import JsonOutputParser,StrOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain.document_loaders import YoutubeLoader
from langchain.chains import LLMChain
from docx import Document as docu
from youtube_transcript_api import YouTubeTranscriptApi


from services.logger import setup_logger
from services.tool_registry import ToolFile
from api.error_utilities import LoaderError


#PowerPoint Loader imports
from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE_TYPE
import os

import google.generativeai as genai
from google.generativeai import GenerativeModel
import PIL
from io import BytesIO
from langchain_core.documents import Document
from typing import List
#Setting up the model for the AI
api_key = os.environ.get('API_KEY')

genai.configure(api_key=api_key)
multimodal_model = GenerativeModel('gemini-1.5-flash')

#HTML and XML loaders
from bs4 import BeautifulSoup

#Extraction of all text from slides in presentation


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

class YouTubeTranscriptLoader:
    def __init__(self, verbose=False):
        self.verbose = verbose


    def fetch_transcript(self, video_id: str) -> str:
        try:
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
            transcript_text = '\n'.join([transcript['text'] for transcript in transcript_list])
            return transcript_text
       
        except Exception as e:
            print(f"Error fetching transcript for video {video_id}: {e}")
            return ""


    def load(self, files: List[ToolFile]):
        documents = []


        for file in files:
            try:
                url = file.url
                video_id = YoutubeLoader.extract_video_id(url)
                transcript_text = self.fetch_transcript(video_id)
            
               
                if transcript_text:
                    documents.append(Document(page_content=transcript_text, metadata={'video_id': video_id}))
                    if self.verbose:
                        print(f"Fetched transcript for video {video_id}")


                else:
                    print(f"No transcript found for video {video_id}")


            except Exception as e:
                print(f"Error loading video {video_id}: {e}")
       
        return documents

class YoutubeLoaders:
    def __init__(self, verbose = False):
        self.verbose = verbose


    def load(self, tool_files: List[ToolFile]):
        documents = []
        youtube_files = []
       
        for file in tool_files:
            url = file.url
           


            if url.lower().startswith("https://youtu.be/"):
                youtube_files.append(file)
   
        yt_loader = YouTubeTranscriptLoader(verbose=self.verbose)
        docs = yt_loader.load(youtube_files)
        if self.verbose:
            print(f"Documents from YouTube loader: {len(docs)}")
        documents.extend(docs)
        if self.verbose:
            print(f"Total documents: {len(documents)}")
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
    
class ImageLoader:
    def __init__(self,files: List[Tuple[BytesIO,str]]):
        self.files = files
    
    def load(self) -> List[Document]:
        documents = []
        text_completion_model = VertexAI(model='gemini-1.5-flash-001')
        prompt= PromptTemplate.from_template("I want you to check if there is any missing words in {text}. If there are any, I want to to autocomplete them with the most relevant word possible and make the whole thing grammatically correct. The output should be a string.")
        text_chain = (
                {"text": RunnablePassthrough()} 
                | prompt 
                | text_completion_model 
                | StrOutputParser()
            )

        for file, file_type in self.files:
            logger.debug(file_type)
            if file_type.lower() in ['jpeg', 'jpg', 'png']:
                logger.info(file)
                image = Image.open(file)
                text = pytesseract.image_to_string(image)
                result = text_chain.invoke({"text" : text})
                metadata = {"source":file_type,"page_number":1}
                document = Document(page_content=result,metadata=metadata)
                documents.append(document)
                    
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
        self.expected_file_types = ["xlsx", "pdf", "pptx", "csv", "docx", "jpeg", 'jpg', "png"]
        self.loader = file_loader or BytesFileXLSXLoader or BytesFilePDFLoader or BytesFileCSVLoader or DocLoader or ImageLoader

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
        self.loaders = [BytesFileXLSXLoader,BytesFilePDFLoader,BytesFileCSVLoader,DocLoader,ImageLoader]
        self.expected_file_types = ["xlsx", "pdf", "pptx", "csv", "docx","jpeg",'jpg',"png"]
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
                        raise LoaderError(f"Expected file types: {string}, but got: {file_type}")

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





class PowerPointLoader:
    def __init__(self,loader = None, verbose=False, expected_file_type="pptx"):
        self.loader = loader
        self.expected_file_type = expected_file_type
        self.verbose = verbose
    def get_slide_text(slides):
        text_concepts = ""
        # Iterate over each shape in the slides collection
        for shape in slides.shapes:
            # Get the title of the slide
            title = ""
            if slides.shapes.title:
                title = slides.shapes.title.text
            texts = ""
            if shape.has_text_frame:
                # Extract text from each paragraph in the text frame
                for paragraph in shape.text_frame.paragraphs:
                    # Extract text from each run in the paragraph
                    for run in paragraph.runs:
                        texts += run.text
            '''elif shape.shape_type == MSO_SHAPE_TYPE.PICTURE:
                image = shape.image
                image_blob = image.blob
                image_file = PIL.Image.open(BytesIO(image_blob))
                logger.info("Writing image in AI")
                response = multimodal_model.generate_content(['Describe the picture', image_file])
                logger.info(response.text)
                texts += response.text'''
            text_concepts += texts
        return title, text_concepts

    def load(self,files: List[ToolFile]) -> List[Document]:
        self.files = files
        
        documents: List[Document] = []
        for tool_file in self.files:
            try:
                url = tool_file.url
                path = urlparse(url).path
                file_type = url.split(".")[-1]
                if file_type not in ('pptx', 'ppt'):
                    raise LoaderError(f"Expected ppt/pptx file but got {file_type}")

                response = requests.get(url, stream=True)
                content = BytesIO(response.content)
                prs = Presentation(content)
                page_content = ""
                
                for slide_num, slide in enumerate(prs.slides, start = 1):
                    title, text_concepts = PowerPointLoader.get_slide_text(slide)
                    
                    page_content += (title + text_concepts)
                
            
                    metadata = {"source": path, "number of slides": slide_num}
                    doc = Document(page_content=page_content, metadata=metadata)
                    documents.append(doc)
                if self.verbose: logger.info(f"Succesfully loaded file from {url}")
            except Exception as e:
                logger.error(f"Failed to load file from {url}")
                logger.error(e)
                continue

        if len(documents) == 0:
            raise LoaderError("Unable to load any files")
        if self.verbose:
            logger.info(f"Loaded {len(documents)} documents")
        return documents
    
class HTMLLoader:
    def __init__(self, expected_file_type="html", verbose=False):
        self.verbose = verbose
        self.expected_file_type = expected_file_type

    def load(self, files: List[Document]) -> List[Document]:
        self.files = files
        
        documents = []
        
        # Ensure file paths is a list
        for tool_file in self.files:
            url = tool_file.url
            response = requests.get(url, stream=True, verify=False)
            if response.status_code != 200:
                raise ValueError(f"Request failed to load file from {url} and got status code {response.status_code}")
            
            html_content = response.content.decode("utf-8")
            soup = BeautifulSoup(html_content, "html.parser")
            text = soup.get_text()
            
            documents.append(Document(page_content=text, metadata={"source": url}))
            logger.info(text)

        return documents

  
class RAGpipeline:
    def __init__(self, loader=None, splitter=None, vectorstore_class=None, embedding_model=None, verbose=False):
        default_config = {
            "loader": HTMLLoader(verbose = verbose), # Creates instance on call with verbosity
            "loader": YoutubeLoaders(verbose=verbose),
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
            for document in documents:
                logger.info(document)
        try:
            self.vectorstore = self.vectorstore_class.from_documents(documents, self.embedding_model)
            logger.info(f"Vectorstore created")
        except Exception as e:
            logger.error(f"Error creating vectorstore: {e}")
            raise  # Rethrow the exception to handle it further
        
        if self.verbose:
            logger.info(f"Vectorstore created")
        
        return self.vectorstore
    
    def compile(self):
        # Compile the pipeline
        self.load_PDFs = RAGRunnable(self.load_PDFs)
        logger.info("Completed loading PDFs - Chuyang Zhang")
        self.split_loaded_documents = RAGRunnable(self.split_loaded_documents)
        logger.info("Completed splitting loaded documents - Chuyang Zhang")
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
