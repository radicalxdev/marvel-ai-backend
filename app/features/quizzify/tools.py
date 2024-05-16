from typing import List, Tuple, Optional
from io import BytesIO
from fastapi import UploadFile
from PyPDF2 import PdfReader
from langchain_core.document_loaders import BaseLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_google_vertexai import VertexAIEmbeddings, VertexAI
from services.schemas import GCS_File
from services.gcp import setup_logger
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field
import json
import os

relative_path = "features/quzzify"

logger = setup_logger()

def read_text_file(file_path):
    # Get the directory containing the script file
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Combine the script directory with the relative file path
    absolute_file_path = os.path.join(script_dir, file_path)

    print(f"Attempting to read file: {absolute_file_path}")
    with open(absolute_file_path, 'r') as file:
        return file.read()

class RAGRunnable:
    def __init__(self, func):
        self.func = func
    
    def __or__(self, other):
        def chained_func(*args, **kwargs):
            # Result of previous function is passed as first argument to next function
            return other(self.func(*args, **kwargs))
        return RAGRunnable(chained_func)
    
    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)

class UploadPDFLoader:
    def __init__(self, files: List[UploadFile]):
        self.files = files

    def load(self) -> List[Document]:
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

class BytesFileLoader:
    def __init__(self, files: List[Tuple[BytesIO, str]]):
        self.files = files
    
    def load(self) -> List[Document]:
        documents = []
        
        for file, file_type in self.files:
            if file_type.lower() == "pdf":
                pdf_reader = PdfReader(file)

                for i, page in enumerate(pdf_reader.pages):
                    page_content = page.extract_text()
                    metadata = {"source": file_type, "page_number": i + 1}

                    doc = Document(page_content=page_content, metadata=metadata)
                    documents.append(doc)
                    
            else:
                raise ValueError(f"Unsupported file type: {file_type}")
            
        return documents

class LocalFileLoader:
    def __init__(self, file_paths: list[str], expected_file_type="pdf"):
        self.file_paths = file_paths
        self.expected_file_type = expected_file_type

    def load(self) -> List[Document]:
        documents = []
        
        # Ensure file paths is a list
        self.file_paths = [self.file_paths] if isinstance(self.file_paths, str) else self.file_paths
    
        for file_path in self.file_paths:
            
            file_type = file_path.split(".")[-1]

            if file_type != self.expected_file_type:
                raise ValueError(f"Expected file type: {self.expected_file_type}, but got: {file_type}")

            with open(file_path, 'rb') as file:
                pdf_reader = PdfReader(file)

                for i, page in enumerate(pdf_reader.pages):
                    page_content = page.extract_text()
                    metadata = {"source": file_path, "page_number": i + 1}

                    doc = Document(page_content=page_content, metadata=metadata)
                    documents.append(doc)

        return documents


class RAGpipeline:
    def __init__(self, loader=None, splitter=None, vectorstore_class=None, embedding_model=None):
        default_config = {
            "loader": UploadPDFLoader,
            "splitter": RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100),
            "vectorstore_class": Chroma,
            "embedding_model": VertexAIEmbeddings(model='textembedding-gecko')
        }
        self.loader = loader or default_config["loader"]
        self.splitter = splitter or default_config["splitter"]
        self.vectorstore_class = vectorstore_class or default_config["vectorstore_class"]
        self.embedding_model = embedding_model or default_config["embedding_model"]

    def load_PDFs(self, files) -> List[Document]:
        loader_instance = self.loader(files)
        total_loaded_files = loader_instance.load()
        return total_loaded_files
    
    def split_loaded_documents(self, loaded_documents: List[Document], verbose=False) -> List[Document]:
        total_chunks = []
        chunks = self.splitter.split_documents(loaded_documents)
        total_chunks.extend(chunks)
        if verbose:
            logger.info(f"Split {len(total_chunks)} chunks")
        return total_chunks
    
    def create_vectorstore(self, documents: List[Document], verbose=False):
        self.vectorstore = self.vectorstore_class.from_documents(documents, self.embedding_model)
        if verbose:
            logger.info(f"Successfully created vectorstore")
        return self.vectorstore
    
    def compile(self):
        # Compile the pipeline
        self.load_PDFs = RAGRunnable(self.load_PDFs)
        self.split_loaded_documents = RAGRunnable(self.split_loaded_documents)
        self.create_vectorstore = RAGRunnable(self.create_vectorstore)
        logger.info(f"Successfully compiled pipeline")
    
    def clear(self):
        return self.vectorstore.delete_collection()
    
    def __call__(self, documents):
        # Returns a vectorstore ready for usage 
        pipeline = self.load_PDFs | self.split_loaded_documents | self.create_vectorstore
        return pipeline(documents)

    
class QuestionChoice(BaseModel):
    key: str = Field(description="A unique identifier for the choice using letters A, B, C, D, etc.")
    value: str = Field(description="The text content of the choice")
class QuizQuestion(BaseModel):
    question: str = Field(description="The question text")
    choices: List[QuestionChoice] = Field(description="A list of choices")
    answer: str = Field(description="The correct answer")
    explanation: str = Field(description="An explanation of why the answer is correct")
class QuizBuilder:
    def __init__(self, vectorstore, topic, prompt=None, model=None, parser=None):
        self.prompt = prompt
        self.vectorstore = vectorstore
        self.model = model
        self.topic = topic
        self.parser = parser
        
        default_config = {
            "model": VertexAI(model="gemini-1.0-pro"),
            "parser": JsonOutputParser(pydantic_object=QuizQuestion)
        }

        if prompt is None:
            config = read_text_file("prompt/quizzify-prompt.txt")
            self.prompt = config
        if vectorstore is None:
            raise ValueError("Vectorstore must be provided")
        if model is None:
            self.model = default_config["model"]
        if topic is None:
            raise ValueError("Topic must be provided")
        if parser is None:
            self.parser = default_config["parser"]
    
    def compile(self):
        # Return the chain
        prompt = PromptTemplate(
            template=self.prompt,
            input_variables=["topic"],
            partial_variables={"format_instructions": self.parser.get_format_instructions()}
        )
        
        retriever = self.vectorstore.as_retriever()
        
        runner = RunnableParallel(
            {"context": retriever, "topic": RunnablePassthrough()}
        )
        
        chain = runner | prompt | self.model | self.parser
        
        return chain
    
    def create_questions(self, num_questions: int = 5) -> List:
        if num_questions > 10:
            return {"message": "error", "data": "Number of questions cannot exceed 10"}
        
        chain = self.compile()
        
        generated_questions = []
        
        while len(generated_questions) < num_questions:
            response = chain.invoke(self.topic)
            generated_questions.append(response)
        
        # Clean up vectorstore process
        self.vectorstore.delete_collection()
        
        return generated_questions

    
        