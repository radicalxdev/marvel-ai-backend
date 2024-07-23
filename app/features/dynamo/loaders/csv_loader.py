import csv
from fastapi import UploadFile
from langchain_core.documents import Document

class CSVLoader:
    def __init__(self, files: list[UploadFile]):
        self.files = files

    def load(self) -> list:
        documents = []

        for upload_file in self.files:
            full_text = []
            with upload_file.file as csv_file:
                csv_file.seek(0)  
                text = csv_file.read().decode('utf-8')  
                reader = csv.reader(text.splitlines())
                for row in reader:
                    full_text.append(", ".join(row))
            content = "\n".join(full_text)
            metadata = {"source": upload_file.filename}
            doc = Document(page_content=content, metadata=metadata)
            documents.append(doc)

        return documents
