__author__  = '1. Sanith Kumar Pallerla'
__email__ = '1. pallerlasanithkumar@gmail.com'
__status__ = 'Development'


from typing import List
from langchain_core.documents import Document
from fastapi import UploadFile

class TextLoader:

    def __init__(self,verbose = None):
        self.verbose = verbose

    def load(self,files : List[UploadFile]) -> List[Document]:
        documents = []

        # Checking whether it's a list of files or not. If not converting it into list of files
        files = [files] if isinstance(files, str) else files

        #variable to keep track of current file
        curent_file_pointer = 0

        #Iterating through each file
        for each_file in files:

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