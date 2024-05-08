from typing import List
from fastapi import UploadFile
from PyPDF2 import PdfReader
from langchain_core.document_loaders import BaseLoader
from langchain_core.documents import Document

class UploadPDFLoader(BaseLoader):
    def __init__(self, file: UploadFile):
        self.upload_file = file
        self.pdf_reader = PdfReader(file.file)
    
    def load(self) -> List[Document]:
        documents = []
        for page in self.pdf_reader.pages:
            doc = Document(
                page_content=page.extract_text(),
                metadata={"source": self.upload_file.filename}
            )
            documents.append(doc)
        return documents