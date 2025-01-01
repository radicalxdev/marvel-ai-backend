from langchain_community.document_loaders import YoutubeLoader
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain_community.document_loaders.csv_loader import CSVLoader
from langchain_community.document_loaders import TextLoader
from langchain_community.document_loaders import UnstructuredURLLoader
from langchain_community.document_loaders import UnstructuredPowerPointLoader
from langchain_community.document_loaders import Docx2txtLoader
from langchain_community.document_loaders import UnstructuredExcelLoader
from langchain_community.document_loaders import UnstructuredXMLLoader
from langchain_google_genai import ChatGoogleGenerativeAI
from app.utils.allowed_file_extensions import FileType
from app.api.error_utilities import FileHandlerError, ImageHandlerError
from langchain.prompts import PromptTemplate
from langchain_google_genai import GoogleGenerativeAI
from app.api.error_utilities import VideoTranscriptError
from langchain_core.messages import HumanMessage
from app.services.logger import setup_logger
from langchain_text_splitters import RecursiveCharacterTextSplitter

import os
import tempfile
import uuid
import requests
import gdown

STRUCTURED_TABULAR_FILE_EXTENSIONS = {"csv", "xls", "xlsx", "gsheet", "xml"}

logger = setup_logger(__name__)

splitter = RecursiveCharacterTextSplitter(
    chunk_size = 1000,
    chunk_overlap = 0
)

def read_text_file(file_path):
    # Get the directory containing the script file
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Combine the script directory with the relative file path
    absolute_file_path = os.path.join(script_dir, file_path)

    with open(absolute_file_path, 'r') as file:
        return file.read()

def build_chain(prompt: str):
    prompt_template = read_text_file(prompt)
    summarize_prompt = PromptTemplate.from_template(prompt_template)

    summarize_model = GoogleGenerativeAI(model="gemini-1.5-flash")

    chain = summarize_prompt | summarize_model 
    return chain

def get_summary(file_url: str, file_type: str, verbose=True):
    file_type = file_type.lower()
    try:
        file_loader = file_loader_map[FileType(file_type)]
        full_content = file_loader(file_url, verbose)
        if file_type in STRUCTURED_TABULAR_FILE_EXTENSIONS:
            prompt = "prompts_for_summarization/summarize_structured_tabular_data_prompt.txt"
        else:
            prompt = "prompts_for_summarization/summarize_text_prompt.txt"

        chain = build_chain(prompt)
        return chain.invoke(full_content)

    except Exception as e:
        logger.error(f"Unsupported file type: {file_type}")
        raise FileHandlerError(f"Unsupported file type", file_url) from e

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


class FileHandlerForGoogleDrive:
    def __init__(self, file_loader, file_extension='docx'):
        self.file_loader = file_loader
        self.file_extension = file_extension

    def load(self, url):
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                unique_filename = os.path.join(temp_dir, f"{uuid.uuid4()}.{self.file_extension}")

                logger.info(f"Downloading file from URL: {url}")

                try:
                    gdown.download(url=url, output=unique_filename, fuzzy=True)
                    logger.info(f"File downloaded successfully to {unique_filename}")
                except Exception as e:
                    logger.error(e)
                    logger.error("File content might be private or unavailable, or the URL is incorrect.")
                    raise FileHandlerError("No file content available") from e

                try:
                    loader = self.file_loader(file_path=unique_filename)
                except Exception as e:
                    logger.error(f"No such file found at {unique_filename}")
                    raise FileHandlerError("No file found", unique_filename) from e

                try:
                    documents = loader.load()
                    logger.info("File loaded successfully.")
                except Exception as e:
                    logger.error(e)
                    logger.error("Error loading file content.")
                    raise FileHandlerError("No file content available") from e

                return documents
        except Exception as e:
            logger.error("An unexpected error occurred during the file handling process.")
            raise e

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

def summarize_transcript_youtube_url(youtube_url: str, max_video_length=600, verbose=False) -> str:
    try:
        loader = YoutubeLoader.from_youtube_url(youtube_url, add_video_info=False)
    except Exception as e:
        logger.error(f"No such video found at {youtube_url}")
        raise VideoTranscriptError(f"No video found", youtube_url) from e

    try:
        docs = loader.load()
    except Exception as e:
        logger.error(f"Video transcript might be private or unavailable in 'en' or the URL is incorrect.")
        raise VideoTranscriptError(f"No video transcripts available", youtube_url) from e

    split_docs = splitter.split_documents(docs)

    full_transcript = [doc.page_content for doc in split_docs]
    full_transcript = " ".join(full_transcript)

    if verbose:
        logger.info(f"Found video")
        logger.info(f"Combined documents into a single string.")
        logger.info(f"Beginning to process transcript...")

    prompt_template = read_text_file("prompts_for_summarization/summarize_youtube_video_prompt.txt")
    summarize_prompt = PromptTemplate.from_template(prompt_template)

    summarize_model = GoogleGenerativeAI(model="gemini-1.5-flash")

    chain = summarize_prompt | summarize_model 

    return chain.invoke(full_transcript)

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
    FileType.XML: load_xml_documents,
    FileType.GDOC: load_gdocs_documents,
    FileType.GSHEET: load_gsheets_documents,
    FileType.GSLIDE: load_gslides_documents,
    FileType.GPDF: load_gpdf_documents
}

llm_for_img = ChatGoogleGenerativeAI(model="gemini-1.5-flash")

def generate_summary_from_img(img_url):
    message = HumanMessage(
    content=[
            {
                "type": "text",
                "text": "Give me a summary of what you see in the image. It must be a detailed paragraph.",
            }, 
            {"type": "image_url", "image_url": img_url},
        ]
    )

    try:
        response = llm_for_img.invoke([message]).content
        logger.info(f"Generated summary: {response}")
    except Exception as e:
        logger.error(f"Error processing the request due to Invalid Content or Invalid Image URL")
        raise ImageHandlerError(f"Error processing the request", img_url) from e

    return response