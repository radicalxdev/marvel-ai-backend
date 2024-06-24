from services.logger import setup_logger
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain_community.document_loaders.csv_loader import CSVLoader
from langchain_community.document_loaders import TextLoader
from langchain_community.document_loaders import UnstructuredURLLoader
from langchain_community.document_loaders import UnstructuredPowerPointLoader
from langchain_community.document_loaders import Docx2txtLoader
from langchain_community.document_loaders import UnstructuredExcelLoader
from langchain_community.document_loaders import UnstructuredXMLLoader
from utils.allowed_file_extensions import FileType, GFileType
import os
import tempfile
import uuid
import requests

from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.output_parsers import JsonOutputParser

from langchain_text_splitters import RecursiveCharacterTextSplitter
from api.error_utilities import FileHandlerError, ImageHandlerError
from langchain.prompts import PromptTemplate
from langchain_google_genai import GoogleGenerativeAI

import gdown


logger = setup_logger(__name__)

splitter = RecursiveCharacterTextSplitter(
    chunk_size = 1000,
    chunk_overlap = 0
)

def build_chain():
    prompt_template = read_text_file("prompt/summarize-prompt.txt")
    summarize_prompt = PromptTemplate.from_template(prompt_template)

    summarize_model = GoogleGenerativeAI(model="gemini-1.5-flash")
        
    chain = summarize_prompt | summarize_model 
    return chain

def get_summary(full_content: str):
    chain = build_chain()
    return chain.invoke(full_content)

def read_text_file(file_path):
    # Get the directory containing the script file
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Combine the script directory with the relative file path
    absolute_file_path = os.path.join(script_dir, file_path)
    
    with open(absolute_file_path, 'r') as file:
        return file.read()

class FileHandler:
    def __init__(self, file_loader, file_extension):
        self.file_loader = file_loader
        self.file_extension = file_extension

    def load(self, url):
        # Generate a unique filename with a UUID prefix
        unique_filename = f"{uuid.uuid4()}.{self.file_extension}"

        # Download the file from the URL and save it to a temporary file
        response = requests.get(url)
        response.raise_for_status()  # Ensure the request was successful

        with tempfile.NamedTemporaryFile(delete=False, prefix=unique_filename) as temp_file:
            temp_file.write(response.content)
            temp_file_path = temp_file.name

        # Use the file_loader to load the documents
        try:
            loader = self.file_loader(file_path=temp_file_path)
        except Exception as e:
            logger.error(f"No such file found at {temp_file_path}")
            raise FileHandlerError(f"No file found", temp_file_path) from e
        
        try:
            documents = loader.load()
        except Exception as e:
            logger.error(f"File content might be private or unavailable or the URL is incorrect.")
            raise FileHandlerError(f"No file content available", temp_file_path) from e

        # Remove the temporary file
        os.remove(temp_file_path)

        return documents

def load_pdf_documents(pdf_url: str, verbose=False):
    pdf_loader = FileHandler(PyPDFLoader, "pdf")
    docs = pdf_loader.load(pdf_url)

    if docs:
        split_docs = splitter.split_documents(docs)

        if verbose:
            logger.info(f"Found PDF file")
            logger.info(f"Splitting documents into {len(split_docs)} chunks")

        full_content = [doc.page_content for doc in split_docs]
        full_content = " ".join(full_content)

        return full_content

def load_csv_documents(csv_url: str, verbose=False):
    csv_loader = FileHandler(CSVLoader, "csv")
    docs = csv_loader.load(csv_url)

    if docs:
        if verbose:
            logger.info(f"Found CSV file")
            logger.info(f"Splitting documents into {len(docs)} chunks")

        full_content = [doc.page_content for doc in docs]
        full_content = " ".join(full_content)

        return full_content

def load_txt_documents(notes_url: str, verbose=False):
    notes_loader = FileHandler(TextLoader, "txt")
    docs = notes_loader.load(notes_url)

    if docs: 
        
        split_docs = splitter.split_documents(docs)
        
        if verbose:
            logger.info(f"Found TXT file")
            logger.info(f"Splitting documents into {len(split_docs)} chunks")

        full_content = [doc.page_content for doc in split_docs]
        full_content = " ".join(full_content)
        
        return full_content

def load_md_documents(notes_url: str, verbose=False):
    notes_loader = FileHandler(TextLoader, "md")
    docs = notes_loader.load(notes_url)
    
    if docs:
        
        split_docs = splitter.split_documents(docs)

        if verbose:
            logger.info(f"Found MD file")
            logger.info(f"Splitting documents into {len(split_docs)} chunks")

        full_content = [doc.page_content for doc in split_docs]
        full_content = " ".join(full_content)
        
        return full_content

def load_url_documents(url: str, verbose=False):
    url_loader = UnstructuredURLLoader(urls=[url])
    docs = url_loader.load()

    if docs:
        split_docs = splitter.split_documents(docs)

        if verbose:
            logger.info(f"Found URL")
            logger.info(f"Splitting documents into {len(split_docs)} chunks")

        full_content = [doc.page_content for doc in split_docs]
        full_content = " ".join(full_content)
        
        return full_content

def load_pptx_documents(pptx_url: str, verbose=False):
    pptx_handler = FileHandler(UnstructuredPowerPointLoader, 'pptx')

    docs = pptx_handler.load(pptx_url)
    if docs: 

        split_docs = splitter.split_documents(docs)

        if verbose:
            logger.info(f"Found PPTX file")
            logger.info(f"Splitting documents into {len(split_docs)} chunks")
        
        full_content = [doc.page_content for doc in split_docs]
        full_content = " ".join(full_content)

        return full_content
        
def load_docx_documents(docx_url: str, verbose=False):
    docx_handler = FileHandler(Docx2txtLoader, 'docx')
    docs = docx_handler.load(docx_url)
    if docs: 

        split_docs = splitter.split_documents(docs)
        
        if verbose:
            logger.info(f"Found DOCX file")
            logger.info(f"Splitting documents into {len(split_docs)} chunks")

        full_content = [doc.page_content for doc in split_docs]
        full_content = " ".join(full_content)
        
        return full_content

def load_xls_documents(xls_url: str, verbose=False):
    xls_handler = FileHandler(UnstructuredExcelLoader, 'xls')
    docs = xls_handler.load(xls_url)
    if docs: 

        split_docs = splitter.split_documents(docs)
        
        if verbose:
            logger.info(f"Found XLS file")
            logger.info(f"Splitting documents into {len(split_docs)} chunks")

        full_content = [doc.page_content for doc in split_docs]
        full_content = " ".join(full_content)
        
        return full_content

def load_xlsx_documents(xlsx_url: str, verbose=False):
    xlsx_handler = FileHandler(UnstructuredExcelLoader, 'xlsx')
    docs = xlsx_handler.load(xlsx_url)
    if docs: 

        split_docs = splitter.split_documents(docs)
        
        if verbose:
            logger.info(f"Found XLSX file")
            logger.info(f"Splitting documents into {len(split_docs)} chunks")

        full_content = [doc.page_content for doc in split_docs]
        full_content = " ".join(full_content)
        
        return full_content

def load_xml_documents(xml_url: str, verbose=False):
    xml_handler = FileHandler(UnstructuredXMLLoader, 'xml')
    docs = xml_handler.load(xml_url)
    if docs: 

        split_docs = splitter.split_documents(docs)
        
        if verbose:
            logger.info(f"Found XML file")
            logger.info(f"Splitting documents into {len(split_docs)} chunks")

        full_content = [doc.page_content for doc in split_docs]
        full_content = " ".join(full_content)
        
        return full_content

file_loader_map = {
    FileType.PDF: load_pdf_documents,
    FileType.CSV: load_csv_documents,
    FileType.TXT: load_txt_documents,
    FileType.MD: load_md_documents,
    FileType.URL: load_url_documents,
    FileType.PPTX: load_pptx_documents,
    FileType.DOCX: load_docx_documents,
    FileType.XLS: load_xls_documents,
    FileType.XLSX: load_xlsx_documents,
    FileType.XML: load_xml_documents
}




class FileHandlerForGoogleDrive:
    def __init__(self, file_loader, file_extension='docx'):
        self.file_loader = file_loader
        self.file_extension = file_extension

    def load(self, url):

        unique_filename = f"{uuid.uuid4()}.{self.file_extension}"

        try:
            gdown.download(url=url, output=unique_filename, fuzzy=True)
        except Exception as e:
            logger.error(f"File content might be private or unavailable or the URL is incorrect.")
            raise FileHandlerError(f"No file content available") from e

        try:
            loader = self.file_loader(file_path=unique_filename)
        except Exception as e:
            logger.error(f"No such file found at {unique_filename}")
            raise FileHandlerError(f"No file found", unique_filename) from e

        try:
            documents = loader.load()
        except Exception as e:
            logger.error(f"File content might be private or unavailable or the URL is incorrect.")
            raise FileHandlerError(f"No file content available") from e

        os.remove(unique_filename)

        return documents
    
def load_gdocs_documents(drive_folder_url: str, verbose=False):

    gdocs_loader = FileHandlerForGoogleDrive(Docx2txtLoader)

    docs = gdocs_loader.load(drive_folder_url)
    
    if docs: 

        split_docs = splitter.split_documents(docs)
        
        if verbose:
            logger.info(f"Found Google Docs files")
            logger.info(f"Splitting documents into {len(split_docs)} chunks")

        full_content = [doc.page_content for doc in split_docs]
        full_content = " ".join(full_content)
        
        return full_content

def load_gsheets_documents(drive_folder_url: str, verbose=False):
    gsheets_loader = FileHandlerForGoogleDrive(UnstructuredExcelLoader, 'xlsx')
    docs = gsheets_loader.load(drive_folder_url)
    if docs: 

        split_docs = splitter.split_documents(docs)

        if verbose:
            logger.info(f"Found Google Sheets files")
            logger.info(f"Splitting documents into {len(split_docs)} chunks")

        full_content = [doc.page_content for doc in split_docs]
        full_content = " ".join(full_content)
        
        return full_content

def load_gslides_documents(drive_folder_url: str, verbose=False):
    gslides_loader = FileHandlerForGoogleDrive(UnstructuredPowerPointLoader, 'pptx')
    docs = gslides_loader.load(drive_folder_url)
    if docs: 

        split_docs = splitter.split_documents(docs)

        if verbose:
            logger.info(f"Found Google Slides files")
            logger.info(f"Splitting documents into {len(split_docs)} chunks")

        full_content = [doc.page_content for doc in split_docs]
        full_content = " ".join(full_content)
        
        return full_content
    
def load_gpdf_documents(drive_folder_url: str, verbose=False):

    gpdf_loader = FileHandlerForGoogleDrive(PyPDFLoader,'pdf')

    docs = gpdf_loader.load(drive_folder_url)
    if docs: 

        if verbose:
            logger.info(f"Found Google PDF files")
            logger.info(f"Splitting documents into {len(docs)} chunks")

        full_content = [doc.page_content for doc in docs]
        full_content = " ".join(full_content)
        
        return full_content


gfile_loader_map = {
    GFileType.DOC: load_gdocs_documents,
    GFileType.SHEET: load_gsheets_documents,
    GFileType.SLIDE: load_gslides_documents,
    GFileType.PDF: load_gpdf_documents
}

llm = ChatGoogleGenerativeAI(model="gemini-pro-vision")

def generate_concepts_from_img(img_url):
    parser = JsonOutputParser(pydantic_object=Flashcard)
    message = HumanMessage(
    content=[
            {
                "type": "text",
                "text": "Give me more than 5 key concepts of what you see in the image",
            },  # You can optionally provide text parts
            {"type": "image_url", "image_url": img_url},
            {"type": "text", "text": f"In this format: {parser.get_format_instructions()}"}
        ]
    )

    try:
        response = llm.invoke([message]).content
        logger.info(f"Generated concepts: {response}")
    except Exception as e:
        logger.error(f"Error processing the request due to Invalid Content or Invalid Image URL")
        raise ImageHandlerError(f"Error processing the request", img_url) from e
    
    return parser.parse(response)


class Flashcard(BaseModel):
    concept: str = Field(description="The concept of the flashcard")
    definition: str = Field(description="The definition of the flashcard")