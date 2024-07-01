from langchain_community.document_loaders import YoutubeLoader, PyPDFLoader
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
from pypdf import PdfReader
from pptx import Presentation
from app.services.logger import setup_logger
import requests
from io import BytesIO
import os


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

class PDFSubLoader():
    def __init__(self, file_content: BytesIO, file_type: str):
        self.file_content = file_content
        self.file_type = file_type
    
    def load(self) -> List[Document]:
        documents = []
        try:
            pdf_reader = PdfReader(self.file_content) #! PyPDF2.PdfReader is deprecated

            for i, page in enumerate(pdf_reader.pages):
                page_content = page.extract_text()
                metadata = {"source": self.file_type, "page_number": i + 1}

                doc = Document(page_content=page_content, metadata=metadata)
                documents.append(doc)
        
        except Exception as e:
                logger.error(f"Failed to load file from PDF sub loader")
                logger.error(e)

        return documents

class PptxSubLoader:
    def __init__(self, file_content: BytesIO, file_type: str):
        self.file_content = file_content
        self.file_type = file_type
    
    def load(self) -> List[Document]:
        documents = []
        try:
            presentation = Presentation(self.file_content)
            for i, slide in enumerate(presentation.slides):
                slide_text = []
                for shape in slide.shapes:
                    if hasattr(shape, "text"):
                        slide_text.append(shape.text)
                
                page_content = "\n".join(slide_text)
                metadata = {"source": self.file_type, "slide_number": i + 1}
                
                doc = Document(page_content=page_content, metadata=metadata)
                documents.append(doc)
        
        except Exception as e:
            logger.error("Failed to load file from PPTX sub loader")
            logger.error(e)

        return documents

class URLLoader:
    def __init__(self, file_loader=None, verbose=False):
        self.loader = file_loader
        self.verbose = verbose

    def load(self, tool_files: List[ToolFile]) -> List[Document]:
        queued_files = []
        documents_list = []
        any_success = False

        for tool_file in tool_files:
            try:
                url = tool_file.url
                response = requests.get(url)
                file_type = tool_file.filename.split(".")[-1]

                # Check response status
                if response.status_code == 200:
                    # Read file
                    file_content = BytesIO(response.content)

                    # Append to Queue
                    queued_files.append((file_content, file_type))
                    if self.verbose:
                        logger.info(f"Successfully loaded file from {url}")

                    any_success = True  # Mark that at least one file was successfully loaded
                else:
                    logger.error(f"Request failed to load file from {url} and got status code {response.status_code}")

            except Exception as e:
                logger.error(f"Failed to load file from {url}")
                logger.error(e)
                continue
        
        # Load file if reponse successful
        if any_success:
            for cur_file_content, cur_file_type in queued_files:
                if cur_file_type == "pdf":
                    self.loader = PDFSubLoader(cur_file_content, cur_file_type)
                elif cur_file_type == "pptx":
                    self.loader = PptxSubLoader(cur_file_content, cur_file_type)
                else:
                    raise LoaderError(f"Unsupported file type: {file_type}")
                document = self.loader.load()
                documents_list.extend(document)

            if self.verbose:
                logger.info(f"Loaded {len(documents_list)} documents")

        if not any_success:
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
    documents = []
    if youtube_url:
        documents.extend(get_youtube_doc(youtube_url))
    if files:
        loader = URLLoader()
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
    
