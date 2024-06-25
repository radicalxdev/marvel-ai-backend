__author__  = '1. Sanith Kumar Pallerla'
__email__ = '1. pallerlasanithkumar@gmail.com'
__status__ = 'Development'


from typing import List
from langchain_core.documents import Document
from fastapi import UploadFile

class TextLoader:

    def __init__(self, files : List[UploadFile]):
        self.files = files

    def load(self) -> List[Document]:
        documents = []

        # Checking whether it's a list of files or not. If not converting it into list of files
        self.files = [self.files] if isinstance(self.files, str) else self.files

        #variable to keep track of current file
        curent_file_pointer = 0

        #Iterating through each file
        for each_file in self.files:

            #Verifying whether the file is a text document or not
            if each_file.lower().endswith('.txt'):

                #Processing file data
                with open(each_file, encoding="utf-8") as file_data:
                    file_content = file_data.read()
                    metadata = {"source":each_file, "file_number": curent_file_pointer+1}
                    doc = Document(page_content=file_content, metadata=metadata)
                    documents.append(doc)
                    file_data.close()

            else:
                raise ValueError(f"Expected file type: .txt, but got: {each_file.split('.')[-1]}")

        return documents