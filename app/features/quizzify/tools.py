from typing import List, Tuple, Dict, Any
from io import BytesIO
from fastapi import UploadFile
from urllib.parse import urlparse
import requests
import os
import json
import time

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_google_genai import GoogleGenerativeAI
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from app.services.logger import setup_logger
from app.services.tool_registry import ToolFile
from app.api.error_utilities import LoaderError
from app.features.quizzify.loaders import BytesFileLoader, WebPageLoader, CustomYoutubeLoader


relative_path = "features/quzzify"

logger = setup_logger(__name__)


def transform_json_dict(input_data: dict) -> dict:
    # Validate and parse the input data to ensure it matches the QuizQuestion schema
    quiz_question = QuizQuestion(**input_data)

    # Transform the choices list into a dictionary
    transformed_choices = {choice.key: choice.value for choice in quiz_question.choices}

    # Create the transformed structure
    transformed_data = {
        "question": quiz_question.question,
        "choices": transformed_choices,
        "answer": quiz_question.answer,
        "explanation": quiz_question.explanation
    }

    return transformed_data


def read_text_file(file_path):
    # Get the directory containing the script file
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Combine the script directory with the relative file path
    absolute_file_path = os.path.join(script_dir, file_path)

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


class URLLoader:
    def __init__(self, file_loader=None, verbose=False):
        self.loader = file_loader or BytesFileLoader
        self.verbose = verbose

    def load(self, files) -> List[Document]:
        queued_files = []
        documents = []
        any_success = False
        files_list = []

        for file in files:
            try:
                url = file.url
                response = requests.get(url)
                parsed_url = urlparse(url)
                path = parsed_url.path

                if response.status_code == 200:
                    # Read file
                    file_content = BytesIO(response.content)

                    # Check file type
                    file_type = path.split(".")[-1]

                    # Append to Queue
                    queued_files.append((file_content, file_type))
                    files_list.append(file)
                    if self.verbose:
                        logger.info(f"Successfully loaded file from {url}")

                    any_success = True  # Mark that at least one file was successfully loaded
                else:
                    logger.error(f"Request failed to load file from {url} and got status code {response.status_code}")

            except Exception as e:
                logger.error(f"Failed to load file from {url}")
                logger.error(e)
                continue

        # Pass Queue to the file loader if there are any successful loads
        if any_success:
            file_loader = self.loader(queued_files, files_list)
            documents = file_loader.load()

            if self.verbose:
                logger.info(f"Loaded {len(documents)} documents")


        return documents

class BaseLoader:

    def __init__(self, verbose = False):
        self.verbose = verbose

    def load(self, files):
        
        documents = []
        file_type_list = ['csv','pptx','docx','pdf','txt']
        youtube_files = []
        webpage_files = []
        other_files = []

        for file in files:
            url = file.url
            file_type = file.filetype
            
            if url.lower().startswith('https://www.youtube.com'):
                youtube_files.append(file)
            elif file_type in file_type_list:
                other_files.append(file)
            elif url.lower().startswith('http://') or url.lower().startswith('https://'):
                webpage_files.append(file)
            else:
                raise ValueError(f"Received {file_type}, Unsupported File Type\n"
                                    f"Supported File Types 'pdf, txt','web page url','pptx','csv','docx','Youtube Url'")


        docs = CustomYoutubeLoader(verbose = self.verbose).load(youtube_files)
        documents.extend(docs)
        docs = WebPageLoader(verbose = self.verbose).load(webpage_files)
        documents.extend(docs)
        docs = URLLoader(verbose = self.verbose).load(other_files)
        documents.extend(docs)
        return documents


class RAGpipeline:
    def __init__(self, loader=None, splitter=None, vectorstore_class=None, embedding_model=None, verbose=False):
        default_config = {
            "loader": BaseLoader(verbose = verbose),
            "splitter": RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100),
            "vectorstore_class": Chroma,
            "embedding_model": GoogleGenerativeAIEmbeddings(model='models/embedding-001')
        }
        self.loader = loader or default_config["loader"]
        self.splitter = splitter or default_config["splitter"]
        self.vectorstore_class = vectorstore_class or default_config["vectorstore_class"]
        self.embedding_model = embedding_model or default_config["embedding_model"]
        self.verbose = verbose


    def load_data(self, files) -> List[Document]:
        if self.verbose:
            logger.info(f"Loading {len(files)} files")
            logger.info(f"Loader type used: {type(self.loader)}")

        logger.debug(f"Loader is a: {type(self.loader)}")

        try:
            total_loaded_files = self.loader.load(files)
        except LoaderError as e:
            logger.error(f"Loader experienced error: {e}")
            raise LoaderError(e)

        return total_loaded_files

    def split_loaded_documents(self, loaded_documents: List[Document]) -> List[Document]:
        if self.verbose:
            logger.info(f"Splitting {len(loaded_documents)} documents")
            logger.info(f"Splitter type used: {type(self.splitter)}")

        total_chunks = []
        chunks = self.splitter.split_documents(loaded_documents)
        total_chunks.extend(chunks)

        if self.verbose: logger.info(f"Split {len(loaded_documents)} documents into {len(total_chunks)} chunks")

        return total_chunks

    def create_vectorstore(self, documents: List[Document]):
        if self.verbose:
            logger.info(f"Creating vectorstore from {len(documents)} documents")

        self.vectorstore = self.vectorstore_class.from_documents(documents, self.embedding_model)

        if self.verbose: logger.info(f"Vectorstore created")
        return self.vectorstore

    def compile(self):
        # Compile the pipeline
        self.load_data = RAGRunnable(self.load_data)
        self.split_loaded_documents = RAGRunnable(self.split_loaded_documents)
        self.create_vectorstore = RAGRunnable(self.create_vectorstore)
        if self.verbose: logger.info(f"Completed pipeline compilation")

    def __call__(self, documents):
        # Returns a vectorstore ready for usage

        if self.verbose:
            logger.info(f"Executing pipeline")
            logger.info(f"Start of Pipeline received: {len(documents)} documents of type {type(documents[0])}")

        pipeline = self.load_data | self.split_loaded_documents | self.create_vectorstore
        return pipeline(documents)


class QuizBuilder:
    def __init__(self, vectorstore, topic, prompt=None, model=None, parser=None, verbose=False):
        default_config = {
            "model": GoogleGenerativeAI(model="gemini-1.0-pro"),
            "parser": JsonOutputParser(pydantic_object=QuizQuestion),
            "prompt": read_text_file("prompt/quizzify-prompt.txt")
        }

        self.prompt = prompt or default_config["prompt"]
        self.model = model or default_config["model"]
        self.parser = parser or default_config["parser"]

        self.vectorstore = vectorstore
        self.topic = topic
        self.verbose = verbose

        if vectorstore is None: raise ValueError("Vectorstore must be provided")
        if topic is None: raise ValueError("Topic must be provided")

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

        if self.verbose: logger.info(f"Chain compilation complete")

        return chain

    def validate_response(self, response: Dict) -> bool:
        try:
            # Assuming the response is already a dictionary
            if isinstance(response, dict):
                if 'question' in response and 'choices' in response and 'answer' in response and 'explanation' in response:
                    choices = response['choices']
                    if isinstance(choices, dict):
                        for key, value in choices.items():
                            if not isinstance(key, str) or not isinstance(value, str):
                                return False
                        return True
            return False
        except TypeError as e:
            if self.verbose:
                logger.error(f"TypeError during response validation: {e}")
            return False

    def format_choices(self, choices: Dict[str, str]) -> List[Dict[str, str]]:
        return [{"key": k, "value": v} for k, v in choices.items()]

    def create_questions(self, num_questions: int = 5) -> List[Dict]:
        if self.verbose: logger.info(f"Creating {num_questions} questions")

        if num_questions > 10:
            return {"message": "error", "data": "Number of questions cannot exceed 10"}

        chain = self.compile()

        generated_questions = []
        attempts = 0
        max_attempts = num_questions * 5  # Allow for more attempts to generate questions

        while len(generated_questions) < num_questions and attempts < max_attempts:
            response = chain.invoke(self.topic)
            if self.verbose:
                logger.info(f"Generated response attempt {attempts + 1}: {response}")

            response = transform_json_dict(response)
            # Directly check if the response format is valid
            if self.validate_response(response):
                response["choices"] = self.format_choices(response["choices"])
                generated_questions.append(response)
                if self.verbose:
                    logger.info(f"Valid question added: {response}")
                    logger.info(f"Total generated questions: {len(generated_questions)}")
            else:
                if self.verbose:
                    logger.warning(f"Invalid response format. Attempt {attempts + 1} of {max_attempts}")

            # Move to the next attempt regardless of success to ensure progress
            attempts += 1

        # Log if fewer questions are generated
        if len(generated_questions) < num_questions:
            logger.warning(f"Only generated {len(generated_questions)} out of {num_questions} requested questions")

        if self.verbose: logger.info(f"Deleting vectorstore")
        self.vectorstore.delete_collection()

        # Return the list of questions
        return generated_questions[:num_questions]


class QuestionChoice(BaseModel):
    key: str = Field(description="A unique identifier for the choice using letters A, B, C, or D.")
    value: str = Field(description="The text content of the choice")


class QuizQuestion(BaseModel):
    question: str = Field(description="The question text")
    choices: List[QuestionChoice] = Field(description="A list of choices for the question, each with a key and a value")
    answer: str = Field(description="The key of the correct answer from the choices list")
    explanation: str = Field(description="An explanation of why the answer is correct")

    model_config = {
        "json_schema_extra": {
            "examples": """ 
                {
                "question": "What is the capital of France?",
                "choices": [
                    {"key": "A", "value": "Berlin"},
                    {"key": "B", "value": "Madrid"},
                    {"key": "C", "value": "Paris"},
                    {"key": "D", "value": "Rome"}
                ],
                "answer": "C",
                "explanation": "Paris is the capital of France."
              }
          """
        }

    }
