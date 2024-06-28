from typing import List, Dict, Union
from io import BytesIO
from fastapi import UploadFile
from pypdf import PdfReader
from pptx import Presentation
from docx import Document as DocumentFromDocx
import pandas as pd
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import urllib.request
import requests
import os
import logging

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import UnstructuredWordDocumentLoader, UnstructuredPowerPointLoader
from langchain_chroma import Chroma
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_google_genai import GoogleGenerativeAI
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from app.services.logger import setup_logger
from app.services.tool_registry import ToolFile
from app.api.error_utilities import LoaderError

from youtube_transcript_api import YouTubeTranscriptApi,NoTranscriptFound,TranscriptsDisabled

relative_path = "features/quzzify"

logger = setup_logger(__name__)
logging.basicConfig(level=logging.INFO)

YOUTUBE_URLS = {
    "youtu.be",
    "m.youtube.com",
    "youtube.com",
    "www.youtube.com",
    "www.youtube-nocookie.com",
    "vid.plus",
}

DOCUMENT_URLS = {
    "pdf",
    "doc",
    "docx",
    "ppt",
    "pptx",
    "txt"
}

SHEET_URLS = {
    "xlsx",
    "csv"
}

def transform_json_dict(input_data: dict) -> dict:
    # Validate and parse the input data to ensure it matches the QuizQuestion schema
    quiz_question = QuizQuestion(**input_data)

    # Transform the choices list into a dictionary
    transformed_choices = {choice.key: choice.value for choice in quiz_question.choices}

    # Create the transformed structure
    transformed_data = {
        "question": quiz_question.question,
        "choices": transformed_choices,
        "answer": quiz_question.answer,
        "explanation": quiz_question.explanation
    }

    return transformed_data

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
    
class BytesFileLoader:
    def __init__(self, files):
        self.files = files
    
    def filter_segments(self,segments,specific_list,section_start,section_end):
        if(specific_list is not None):
            filtered_segments = [doc for doc in segments if doc.metadata['page_number'] in specific_list]
        else:
            filtered_segments = [doc for doc in segments if section_start <= doc.metadata['page_number'] <= section_end]
        return filtered_segments
    
    def add_doc(self,page_content,file_type,number):
        metadata = {'source': file_type, 'page_number': number}
        doc = Document(page_content=page_content,metadata = metadata)
        return doc
        
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
                    
            else:
                raise ValueError(f"Unsupported file type: {file_type}")
    
class SheetLoader:
    def __init__(self, file):
        self.file_content, self.file_type,self.specific_list, self.section_start, self.section_end = file
        
    def parse_section(self, section):
        if isinstance(section, (int, float)):
            return int(section), 0  
        elif isinstance(section, list):
            return int(section[0]), int(section[1])
        else:
            raise ValueError(f"Invalid section format: {section}")
        
    def load(self):
        
        documents = []
        
        if(self.file_type == "xlsx"):
            df = pd.read_excel(self.file_content)
        elif(self.file_type == "csv"):
            df = pd.read_csv(self.file_content)

        start_row, start_col = self.parse_section(self.section_start)
        end_row, end_col = self.parse_section(self.section_end)

        row_start = max(0, min(start_row, end_row, len(df) - 1))
        row_end = min(len(df) - 1, max(start_row, end_row))
        col_start = max(0, min(start_col, end_col, len(df.columns) - 1))
        col_end = min(len(df.columns) - 1, max(start_col, end_col))

        filtered_df = df.iloc[row_start:row_end + 1, col_start:col_end + 1]

        for index, row in filtered_df.iterrows():
            filtered_text = row.to_string()
            metadata = {
                "row": index,
                "columns": ", ".join(filtered_df.columns)  
            }
            documents.append(Document(page_content=filtered_text, metadata=metadata))
        
        return documents
    
class DocumentLoader(BytesFileLoader):
    def __init__(self, file):
        self.file_content, self.file_type,self.specific_list, self.section_start, self.section_end = file
     
    def load(self):
        
        documents = []
        segments = []
        
        if(self.file_type == "pdf"):
            
            pdf_reader = PdfReader(self.file_content) #! PyPDF2.PdfReader is deprecated

            for i, page in enumerate(pdf_reader.pages):
                
                page_content = page.extract_text()
                segments.append(self.add_doc(page_content,self.file_type,i + 1))
                
        if(self.file_type in ["doc","ppt"]):
            
            logger.warning('''Specific pages/slides are not implemented for doc/ppt files. 
            Convert to docx/pptx for specific pages''')
            temp_name = f"temp.{self.file_type}"
            with open(temp_name, 'wb') as temp_file:
                temp_file.write(self.file_content.getbuffer())
            if(self.file_type == "doc"):
                loader = UnstructuredWordDocumentLoader(temp_name)
            else:
                loader = UnstructuredPowerPointLoader(temp_name)
            doc = loader.load()
            documents.extend(doc)
            os.unlink(temp_name)
            
            return documents
        
        elif(self.file_type == "docx"):
            
            doc = DocumentFromDocx(self.file_content)
            doc_text = []
            for paragraph in doc.paragraphs:
                doc_text.append(paragraph.text)
            current_page = []
            word_count = 0 
            words_per_page = 500
            page_number = 1
            for para in doc_text:
                word_count += len(para.split())
                current_page.append(para)
                if word_count >= words_per_page:
                    page_content = " ".join(current_page)
                    segments.append(self.add_doc(page_content,self.file_type,page_number))
                    current_page = []
                    word_count = 0
                    page_number += 1
            if current_page:
                segments.append(self.add_doc(page_content,self.file_type,page_number))
                page_number += 1
                
        elif(self.file_type == "pptx"):
            
            presentation = Presentation(self.file_content)
    
            for i, slide in enumerate(presentation.slides):
                # Extract text from the slide
                slide_content = '\n'.join(shape.text for shape in slide.shapes if hasattr(shape, "text"))
                segments.append(self.add_doc(slide_content,self.file_type,i + 1))
    
        elif(self.file_type == "txt"):
            
            try:
                txt_content = self.file_content.getvalue().decode("utf-8")
            except UnicodeDecodeError:
                txt_content = self.file_content.getvalue().decode("latin-1")

            words_per_page = 500
            words = txt_content.split()
            num_words = len(words)
            num_pages = (num_words // words_per_page) + (1 if num_words % words_per_page > 0 else 0)

            for i in range(num_pages):
                start_idx = i * words_per_page
                end_idx = min((i+1) * words_per_page, num_words)
                page_content = ' '.join(words[start_idx:end_idx])
                segments.append(self.add_doc(page_content,self.file_type,i + 1))
        
        filtered_segments = self.filter_segments(segments,self.specific_list,self.section_start,self.section_end)  
        documents.extend(filtered_segments)
        
        return documents
    
class WebPageLoader(BytesFileLoader):
    def __init__(self, file):
        self.file_content, self.file_type,self.specific_list, self.section_start, self.section_end = file

    def load(self) -> List[Document]:
        
        documents = []
        
        try:
            user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
            headers={'User-Agent':user_agent,} 
            request = urllib.request.Request(self.file_content,None,headers)
            html = urllib.request.urlopen(request).read()
            web_text = ' '.join(BeautifulSoup(html, "html.parser").stripped_strings)
            segments = []
            
            words_per_page = 500
            words = web_text.split()
            num_words = len(words)
            num_pages = (num_words // words_per_page) + (1 if num_words % words_per_page > 0 else 0)

            for i in range(num_pages):
                start_idx = i * words_per_page
                end_idx = min((i+1) * words_per_page, num_words)
                page_content = ' '.join(words[start_idx:end_idx])
                metadata = {'source': self.file_type, 'page_number': i + 1}
                doc = Document(page_content=page_content,metadata = metadata)
                segments.append(doc)
            
            filtered_segments = self.filter_segments(segments,self.specific_list,self.section_start,self.section_end)
            documents.extend(filtered_segments)
            
            return documents
                
        except Exception as e:
            logger.error(f"Failed to load content from {self.file_content}")
            logger.error(e)
                
class YouTubeLoader:
    
    def __init__(self, file):
        self.file_content, self.file_type,self.specific_list, self.section_start, self.section_end = file
    
    def load(self):
        
        documents = []
        
        video_id = self.file_content.split("v=")[1].split("&")[0]
        logger.info(f"Processing Youtube Video ID: {video_id}")
        
        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        except TranscriptsDisabled:
            logger.error(f"Transcripts are disabled for video ID: {video_id}")

        try:
            transcript = transcript_list.find_transcript(["en"])

        except NoTranscriptFound:
            logger.error(f"No English transcript found for video ID: {video_id}")

        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        segments = []
        for entry in transcript:
            metadata = {
                'source': 'youtube',
                'video_id': video_id,
                'start_time': entry['start'],
                'duration': entry['duration']
            }
            doc = Document(page_content=entry['text'],metadata = metadata)
            segments.append(doc)
        
        filtered_segments = [doc for doc in segments if self.section_start <= doc.metadata['start_time'] <= self.section_end]
        documents.extend(filtered_segments)
        
        return documents

class URLLoader:
    def __init__(self, file_loader=None, expected_file_type="pdf", verbose=False):
        self.loader = file_loader or BytesFileLoader
        self.expected_file_type = expected_file_type
        self.verbose = verbose

    def load(self, tool_files: List[ToolFile]) -> List[Document]:

        documents = []
        any_success = False

        for tool_file in tool_files:
            try:
                url = tool_file.url
                response = requests.get(url)
                parsed_url = urlparse(url)
                path = parsed_url.path
                self.expected_file_type = tool_file.file_type
                section_start = tool_file.section_start
                section_end = tool_file.section_end or float('inf')
                specific_list = tool_file.specific_list
                if(type(section_start) == float):
                    if(section_start >= section_end):
                        raise LoaderError(f"section_start must be less than section_end")
                    if(section_start < 0):
                        section_start = 0
                
                if response.status_code == 200:
                    
                    # Check file type
                    if(parsed_url.netloc in YOUTUBE_URLS):
                        file_type = "youtube"
                        file_content = url
                    elif(path.split(".")[-1] in set.union(SHEET_URLS,DOCUMENT_URLS)):
                        file_type = path.split(".")[-1]
                        # Read file
                        file_content = BytesIO(response.content)
                    elif("http" in url):
                        file_type = "web_url"
                        file_content = url
                        
                    if file_type != self.expected_file_type:
                        raise LoaderError(f"Expected file type: {self.expected_file_type}, but got: {file_type}")

                    # Append to Queue
                    file = (file_content, file_type, specific_list, section_start, section_end)
                    if(file_type in DOCUMENT_URLS):
                        self.loader = DocumentLoader
                    elif(file_type in SHEET_URLS):
                        self.loader = SheetLoader
                    elif(file_type == "web_url"):
                        self.loader = WebPageLoader
                    elif(file_type == "youtube"):
                        self.loader = YouTubeLoader
                    else:
                        raise ValueError(f"Unsupported file type: {file_type}")

                    if self.verbose:
                        logger.info(f"Successfully loaded file from {url}")

                    any_success = True
                    
                    logger.info(f"Loading file")
                    file_loader = self.loader(file)
                    logger.debug(f"File loader is a: {type(file_loader)}")
                    documents.extend(file_loader.load())
                    if self.verbose:
                        logger.info(f"Loaded {len(documents)} documents")
                    
                else:
                    logger.error(f"Request failed to load file from {url} and got status code {response.status_code}")

            except Exception as e:
                logger.error(f"Failed to load file from {url}")
                logger.error(e)
                continue

        if not any_success:
            raise LoaderError("Unable to load any files from URLs")

        return documents


class RAGpipeline:
    def __init__(self, loader=None, splitter=None, vectorstore_class=None, embedding_model=None, verbose=False):
        default_config = {
            "loader": URLLoader(verbose = verbose), # Creates instance on call with verbosity
            "splitter": RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100),
            "vectorstore_class": Chroma,
            "embedding_model": GoogleGenerativeAIEmbeddings(model='models/embedding-001')
        }
        self.loader = loader or default_config["loader"]
        self.splitter = splitter or default_config["splitter"]
        self.vectorstore_class = vectorstore_class or default_config["vectorstore_class"]
        self.embedding_model = embedding_model or default_config["embedding_model"]
        self.verbose = verbose

    def load_docs(self, files) -> List[Document]:
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
        self.load_docs = RAGRunnable(self.load_docs)
        self.split_loaded_documents = RAGRunnable(self.split_loaded_documents)
        self.create_vectorstore = RAGRunnable(self.create_vectorstore)
        if self.verbose: logger.info(f"Completed pipeline compilation")
    
    def __call__(self, documents):
        # Returns a vectorstore ready for usage 
        
        if self.verbose: 
            logger.info(f"Executing pipeline")
            logger.info(f"Start of Pipeline received: {len(documents)} documents of type {type(documents[0])}")
        
        pipeline = self.load_docs | self.split_loaded_documents | self.create_vectorstore
        return pipeline(documents)

class QuizBuilder:
    def __init__(self, vectorstore, topic, prompt=None, model=None, parser=None, verbose=False):
        default_config = {
            "model": GoogleGenerativeAI(model="gemini-1.0-pro"),
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

            response = transform_json_dict(response)
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
    key: str = Field(description="A unique identifier for the choice using letters A, B, C, or D.")
    value: str = Field(description="The text content of the choice")
class QuizQuestion(BaseModel):
    question: str = Field(description="The question text")
    choices: List[QuestionChoice] = Field(description="A list of choices for the question, each with a key and a value")
    answer: str = Field(description="The key of the correct answer from the choices list")
    explanation: str = Field(description="An explanation of why the answer is correct")

    model_config = {
        "json_schema_extra": {
            "examples": """ 
                {
                "question": "What is the capital of France?",
                "choices": [
                    {"key": "A", "value": "Berlin"},
                    {"key": "B", "value": "Madrid"},
                    {"key": "C", "value": "Paris"},
                    {"key": "D", "value": "Rome"}
                ],
                "answer": "C",
                "explanation": "Paris is the capital of France."
              }
          """
        }

      }

