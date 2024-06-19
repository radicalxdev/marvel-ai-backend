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
from langchain_google_community import GoogleDriveLoader
from langchain_googledrive.document_loaders import GoogleDriveLoader as GoogleDriveLoader2
from utils.allowed_file_extensions import FileType, GFileType
from utils.extract_gdrive_folder_id import extract_folder_id
import os
import tempfile
import uuid
import requests

from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.output_parsers import JsonOutputParser

logger = setup_logger(__name__)

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
        loader = self.file_loader(file_path=temp_file_path)
        documents = loader.load()

        # Remove the temporary file
        os.remove(temp_file_path)

        return documents

def load_pdf_documents(pdf_url: str):
    pdf_loader = FileHandler(PyPDFLoader, "pdf")
    pages = pdf_loader.load(pdf_url)
    print(pages)

def load_csv_documents(csv_url: str):
    csv_loader = FileHandler(CSVLoader, "csv")
    pages = csv_loader.load(csv_url)
    print(pages)

def load_txt_documents(notes_url: str):
    notes_loader = FileHandler(TextLoader, "txt")
    pages = notes_loader.load(notes_url)
    print(pages)

def load_md_documents(notes_url: str):
    notes_loader = FileHandler(TextLoader, "md")
    pages = notes_loader.load(notes_url)
    print(pages)

def load_url_documents(url: str):
    url_loader = UnstructuredURLLoader([url])
    pages = url_loader.load()
    print(pages)

def load_pptx_documents(pptx_url: str):
    pptx_handler = FileHandler(UnstructuredPowerPointLoader, 'pptx')
    pages = pptx_handler.load(pptx_url)
    print(pages)

def load_docx_documents(docx_url: str):
    docx_handler = FileHandler(Docx2txtLoader, 'docx')
    pages = docx_handler.load(docx_url)
    print(pages)

def load_xls_documents(xls_url: str):
    xls_handler = FileHandler(UnstructuredExcelLoader, 'xls')
    pages = xls_handler.load(xls_url)
    print(pages)

def load_xlsx_documents(xlsx_url: str):
    xlsx_handler = FileHandler(UnstructuredExcelLoader, 'xlsx')
    pages = xlsx_handler.load(xlsx_url)
    print(pages)

def load_xml_documents(xml_url: str):
    xml_handler = FileHandler(UnstructuredXMLLoader, 'xml')
    pages = xml_handler.load(xml_url)
    print(pages)

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
    def __init__(self, file_loader=GoogleDriveLoader, file_type='document'):
        self.file_loader = file_loader
        self.file_type = file_type

    def load(self, url):

        file_id = extract_folder_id(url)

        loader = self.file_loader(
            credentials_path=os.getcwd()+'\credentials.json',
            token_path=os.getcwd()+'\google_token.json',
            folder_id=file_id,
            file_types=[self.file_type],
            recursive=False,
        )

        documents = loader.load()

        return documents
    
def load_gdocs_documents(drive_folder_url: str):
    gdocs_loader = FileHandlerForGoogleDrive(file_type="document")
    pages = gdocs_loader.load(drive_folder_url)
    print(pages)

def load_gsheets_documents(drive_folder_url: str):
    gsheets_loader = FileHandlerForGoogleDrive(file_type="sheet")
    pages = gsheets_loader.load(drive_folder_url)
    print(pages)

def load_gslides_documents(drive_folder_url: str):

    file_id = extract_folder_id(drive_folder_url)

    gslides_loader = GoogleDriveLoader2(
        folder_id=file_id,
        file_types=['application/vnd.google-apps.presentation'],
        recursive=False,
    )

    pages = gslides_loader.load()
    print(pages)


gfile_loader_map = {
    GFileType.DOC: load_gdocs_documents,
    GFileType.SHEET: load_gsheets_documents,
    GFileType.SLIDE: load_gslides_documents
}



llm = ChatGoogleGenerativeAI(model="gemini-pro-vision")

def generate_concepts_from_img(img_url):
    parser = JsonOutputParser(pydantic_object=Flashcard)
    message = HumanMessage(
    content=[
            {
                "type": "text",
                "text": "Give me the key concepts of what you see in the image",
            },  # You can optionally provide text parts
            {"type": "image_url", "image_url": img_url},
            {"type": "text", "text": f"In this format: {parser.get_format_instructions()}"}
        ]
    )
    response = llm.invoke([message]).content
    return parser.parse(response)


class Flashcard(BaseModel):
    concept: str = Field(description="The concept of the flashcard")
    definition: str = Field(description="The definition of the flashcard")