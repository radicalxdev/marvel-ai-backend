from fastapi import UploadFile
from typing import List


def executor(upload_files: List[UploadFile]):
    from features.quizzify.tools import UploadPDFLoader
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    
    total_loaded_files = []
    
    for file in upload_files:
        reader = UploadPDFLoader(file)
        documents = reader.load()
        total_loaded_files.append(documents)
    
    print(f"Read {len(total_loaded_files)} documents")
    print(f"Type of single doc: {type(total_loaded_files[0][0])}")
    print(f"Length of loaded file: {len(total_loaded_files[0])}")
    
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    
    total_chunks = []
    
    for file in total_loaded_files:
        chunks = text_splitter.split_documents(file)
        total_chunks.extend(chunks)
        print(f"Split into {len(chunks)} chunks")
    
    print(f"Total chunks: {len(total_chunks)}")
    
    return {"message": "success"}