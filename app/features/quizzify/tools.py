from typing import List
from fastapi import UploadFile
from PyPDF2 import PdfReader
from langchain_core.document_loaders import BaseLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_google_vertexai import VertexAIEmbeddings, VertexAI
from services.gcp import setup_logger, read_blob_to_string
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field

logger = setup_logger()

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

class RAGpipeline:
    def __init__(self, loader=None, splitter=None, vectorstore_class=None, embedding_model=None):
        self.loader = loader
        self.splitter = splitter
        self.vectorstore_class = vectorstore_class
        self.vectorstore = None
        self.embedding_model = embedding_model
        
        default_config = {
            "loader": UploadPDFLoader,
            "splitter": RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100),
            "vectorstore_class": Chroma,
            "embedding_model": VertexAIEmbeddings(model='textembedding-gecko')
        }
        if loader is None:
            self.loader = default_config["loader"]
        if splitter is None:
            self.splitter = default_config["splitter"]
        if vectorstore_class is None:
            self.vectorstore_class = default_config["vectorstore_class"]
        if embedding_model is None:
            self.embedding_model = default_config["embedding_model"]

    def load_PDFs(self, files: List[UploadFile], datatype="raw", verbose=False) -> List[Document]:
        total_loaded_files = []
        
        if datatype in ["raw", "path"]: # Allow file path later
            if datatype == "raw":
                # The UploadPDFLoader returns a list of UploadFile documents
                total_loaded_files = self.loader(files).load()
            
            if verbose:
                logger.info(f"Loaded {len(total_loaded_files)} files")
            return total_loaded_files
        
        else: 
            raise ValueError(f"Unknown datatype for loading: {datatype}")
    
    def split_loaded_documents(self, loaded_documents: List[Document], verbose = False) -> List[Document]:
        total_chunks = []
        chunks = self.splitter.split_documents(loaded_documents)
        total_chunks.extend(chunks)
        if verbose:
            logger.info(f"Split {len(total_chunks)} chunks")
        return total_chunks
    
    def create_vectorstore(self, documents: List[Document], verbose = False):
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
    key: str = Field(description="A unique identifier for the choice")
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
            self.prompt = read_blob_to_string(bucket_name="backend-prompt-lib", file_path="quizzify/quizzify-prompt.txt")
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
    
    def create_questions(self, num_questions=5) -> List:
        if num_questions > 10:
            return {"message": "error", "data": "Number of questions cannot exceed 10"}
        
        chain = self.compile()
        
        generated_questions = []
        
        while len(generated_questions) < num_questions:
            response = chain.invoke(self.topic)
            generated_questions.append(response)
        
        return generated_questions
    
        