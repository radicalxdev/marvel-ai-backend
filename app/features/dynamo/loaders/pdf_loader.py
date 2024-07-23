from pypdf import PdfReader
from fastapi import UploadFile
from langchain_core.documents import Document

class PDFLoader:
    def __init__(self, files: list[UploadFile]):
        self.files = files

    def load(self) -> list:
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