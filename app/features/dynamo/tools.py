from langchain_community.document_loaders import YoutubeLoader, PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.prompts import PromptTemplate
from langchain_google_genai import GoogleGenerativeAI
from langchain_core.output_parsers import JsonOutputParser
from langchain.chains.summarize import load_summarize_chain
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.documents import Document
from app.services.tool_registry import ToolFile
from app.api.error_utilities import LoaderError
from typing import List, Tuple, Dict, Any
from app.api.error_utilities import VideoTranscriptError
from fastapi import HTTPException
from app.services.logger import setup_logger
import requests
import os

from docx import Document as DocxDocument
import json
import csv
from io import BytesIO
from pypdf import PdfReader

logger = setup_logger(__name__)

# AI Model
model = GoogleGenerativeAI(model="gemini-1.0-pro")

def read_text_file(file_path):
    # Get the directory containing the script file
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Combine the script directory with the relative file path
    absolute_file_path = os.path.join(script_dir, file_path)
    
    with open(absolute_file_path, 'r') as file:
        return file.read()

class PDFSubLoader:
    def __init__(self, file_url: str):
        self.file_url = file_url

    def load(self) -> List[Document]:
        documents = []
        try:
            response = requests.get(self.file_url)
            if response.status_code == 200:
                file_content = BytesIO(response.content)

                pdf_reader = PdfReader(file_content) 

                for i, page in enumerate(pdf_reader.pages):
                    page_content = page.extract_text()
                    metadata = { "page_number": i + 1}

                    doc = Document(page_content=page_content, metadata=metadata)
                    documents.append(doc)

            else:
                logger.error(f"Failed to load PDF from {self.file_url}: HTTP status code {response.status_code}")

        except Exception as e:
            logger.error(f"Failed to load file from PDF sub loader: {e}")

        return documents

class TextSubLoader:
    def __init__(self, url: str):
        self.url = url

    def load(self) -> List[Document]:
        response = requests.get(self.url)
        if response.status_code == 200:
            file_content = BytesIO(response.content)
            text = file_content.read().decode('utf-8')
            doc = Document(page_content=text, metadata={"source": self.url})
            return [doc]
        else:
            logger.error(f"Failed to load text file from {self.url}")
            return []

class JsonSubLoader:
    def __init__(self, url: str):
        self.url = url

    def load(self) -> List[Document]:
        response = requests.get(self.url)
        if response.status_code == 200:
            file_content = BytesIO(response.content)
            data = json.load(file_content)
            content = json.dumps(data, indent=2)
            doc = Document(page_content=content, metadata={"source": self.url})
            return [doc]
        else:
            logger.error(f"Failed to load JSON file from {self.url}")
            return []

class MarkdownSubLoader:
    def __init__(self, url: str):
        self.url = url

    def load(self) -> List[Document]:
        response = requests.get(self.url)
        if response.status_code == 200:
            file_content = BytesIO(response.content)
            content = file_content.read().decode('utf-8')
            doc = Document(page_content=content, metadata={"source": self.url})
            return [doc]
        else:
            logger.error(f"Failed to load Markdown file from {self.url}")
            return []

class DocxSubLoader:
    def __init__(self, url: str, azure_endpoint: str, azure_api_key: str):
        self.url = url
        self.azure_endpoint = azure_endpoint
        self.azure_api_key = azure_api_key

    def load(self) -> List[Document]:
        documents = []
        try:
            response = requests.get(self.url)
            if response.status_code == 200:
                file_content = BytesIO(response.content)
                docx_document = DocxDocument(file_content)
                full_text = []
                for paragraph in docx_document.paragraphs:
                    full_text.append(paragraph.text)
                content = '\n'.join(full_text)
                doc = Document(page_content=content, metadata={"source": self.url})
                documents.append(doc)
            else:
                logger.error(f"Failed to load DOCX file from {self.url}")

        except Exception as e:
            logger.error(f"Failed to load DOCX file: {e}")

        return documents

class CsvSubLoader:
    def __init__(self, url: str):
        self.url = url

    def load(self) -> List[Document]:
        response = requests.get(self.url)
        if response.status_code == 200:
            file_content = BytesIO(response.content)
            file_content.seek(0)
            reader = csv.reader(file_content.decode('utf-8').splitlines())
            content = '\n'.join([', '.join(row) for row in reader])
            doc = Document(page_content=content, metadata={"source": self.url})
            return [doc]
        else:
            logger.error(f"Failed to load CSV file from {self.url}")
            return []

class HtmlSubLoader:
    def __init__(self, url: str):
        self.url = url

    def load(self) -> List[Document]:
        response = requests.get(self.url)
        if response.status_code == 200:
            file_content = BytesIO(response.content)
            content = file_content.read().decode('utf-8')
            doc = Document(page_content=content, metadata={"source": self.url})
            return [doc]
        else:
            logger.error(f"Failed to load HTML file from {self.url}")
            return []

class PPTSubLoader:
    def __init__(self, url: str):
        self.url = url
    
    def load(self) -> List[Document]:
        pass


class URLLoader:
    def __init__(self, file_loader=None, verbose=False):
        self.loader = file_loader
        self.verbose = verbose

    def load(self, tool_files: List[ToolFile]) -> List[Document]:
        documents_list = []

        for tool_file in tool_files:
            try:
                url = tool_file.url
                file_type = tool_file.filename.split(".")[-1].lower()

                if file_type == "pdf":
                    self.loader = PDFSubLoader(url)
                elif file_type == "txt":
                    self.loader = TextSubLoader(url)
                elif file_type == 'json':
                    self.loader = JsonSubLoader(url)
                elif file_type == 'md':
                    self.loader = MarkdownSubLoader(url)
                elif file_type in ["doc", "docx"]:
                    self.loader = DocxSubLoader(url, azure_endpoint='https://dynamo.cognitiveservices.azure.com/', azure_api_key='c9c3c358e15f4908affe1f1fcfae6e49')
                elif file_type == 'csv':
                    self.loader = CsvSubLoader(url)
                elif file_type == 'html':
                    self.loader = HtmlSubLoader(url)
                elif file_type in ['ppt', 'pptx']:
                    self.loader = PPTSubLoader(url)
                else:
                    logger.error(f"Unsupported file type: {file_type}")
                    continue

                document = self.loader.load()
                if document:
                    documents_list.extend(document)
                    if self.verbose:
                        logger.info(f"Successfully loaded file from {url}, type {file_type}")

            except Exception as e:
                logger.error(f"Failed to load file from {url}: {e}")

        if not documents_list:
            raise LoaderError("Unable to load any files from URLs")

        return documents_list


def get_youtube_doc(youtube_url: str, max_video_length=600, verbose=False) -> List[Document]:
    try:
        loader = YoutubeLoader.from_youtube_url(youtube_url, add_video_info=True)
    except Exception as e:
        logger.error(f"No such video found at {youtube_url}")
        raise VideoTranscriptError(f"No video found", youtube_url) from e
    
    try:
        docs = loader.load()
        length = docs[0].metadata["length"]
        title = docs[0].metadata["title"]
        if length > max_video_length:
            raise VideoTranscriptError(f"Video is {length} seconds long, please provide a video less than {max_video_length} seconds long", youtube_url)

        if verbose:
            logger.info(f"Found video with title: {title} and length: {length}")
            logger.info(f"Generate documents from youtube video.")
        
        return docs
    
    except Exception as e:
        logger.error(f"Video transcript might be private or unavailable in 'en' or the URL is incorrect.")
        raise VideoTranscriptError(f"No video transcripts available", youtube_url) from e

def summarize_docs(documents) -> str:
    try:
        summarize_model = GoogleGenerativeAI(model="gemini-1.5-flash")
        chain = load_summarize_chain(summarize_model, chain_type="map_reduce")
        result = chain.invoke(documents)
    
    except Exception as e:
        logger.error(f"Summarize error: {e}")
    
    # TODO 
    # Evaluate Summary Quality
    
    return result["output_text"]

def load_documents(youtube_url: str, files: list[ToolFile]):
    logger.info(f'Files: {files}')
    documents = []
    if youtube_url:
        documents.extend(get_youtube_doc(youtube_url))
    if files:
        loader = URLLoader(verbose=True)
        docs = loader.load(files)
        documents.extend(docs)
    
    return documents

# Summarize chain
def summarize_transcript(youtube_url: str, max_video_length=600, verbose=False) -> str:
    try:
        loader = YoutubeLoader.from_youtube_url(youtube_url, add_video_info=True)
    except Exception as e:
        logger.error(f"No such video found at {youtube_url}")
        raise VideoTranscriptError(f"No video found", youtube_url) from e
    
    try:
        docs = loader.load()
        length = docs[0].metadata["length"]
        title = docs[0].metadata["title"]
    except Exception as e:
        logger.error(f"Video transcript might be private or unavailable in 'en' or the URL is incorrect.")
        raise VideoTranscriptError(f"No video transcripts available", youtube_url) from e
    
    splitter = RecursiveCharacterTextSplitter(
        chunk_size = 1000,
        chunk_overlap = 0
    )
    
    split_docs = splitter.split_documents(docs)
    
    full_transcript = [doc.page_content for doc in split_docs]
    full_transcript = " ".join(full_transcript)

    full_transcript = [doc.page_content for doc in split_docs]
    full_transcript = " ".join(full_transcript)

    if length > max_video_length:
        raise VideoTranscriptError(f"Video is {length} seconds long, please provide a video less than {max_video_length} seconds long", youtube_url)

    if verbose:
        logger.info(f"Found video with title: {title} and length: {length}")
        logger.info(f"Combined documents into a single string.")
        logger.info(f"Beginning to process transcript...")
    
    prompt_template = read_text_file("prompt/summarize-prompt.txt")
    summarize_prompt = PromptTemplate.from_template(prompt_template)

    summarize_model = GoogleGenerativeAI(model="gemini-1.5-flash")
    
    chain = summarize_prompt | summarize_model 
    
    return chain.invoke(full_transcript)

def generate_flashcards(summary: str, verbose=False) -> list:
    # Receive the summary from the map reduce chain and generate flashcards
    parser = JsonOutputParser(pydantic_object=Flashcard)
    
    if verbose: logger.info(f"Beginning to process flashcards from summary")
    
    template = read_text_file("prompt/dynamo-prompt.txt")
    examples = read_text_file("prompt/examples.txt")
    
    cards_prompt = PromptTemplate(
        template=template,
        input_variables=["summary", "examples"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )
    
    cards_chain = cards_prompt | model | parser
    
    try:
        response = cards_chain.invoke({"summary": summary, "examples": examples})
    except Exception as e:
        logger.error(f"Failed to generate flashcards: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate flashcards from LLM")
    
    return response

class Flashcard(BaseModel):
    concept: str = Field(description="The concept of the flashcard") 
    definition: str = Field(description="The definition of the flashcard")