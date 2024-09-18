from typing import List, Dict
import os

from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_google_genai import GoogleGenerativeAI
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from app.services.logger import setup_logger

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

class QuizBuilder:
    def __init__(self, topic, lang='en', file_type=None, vectorstore_class=Chroma, prompt=None, embedding_model=None, model=None, parser=None, verbose=False):
        default_config = {
            "model": GoogleGenerativeAI(model="gemini-1.0-pro"),
            "embedding_model": GoogleGenerativeAIEmbeddings(model='models/embedding-001'),
            "parser": JsonOutputParser(pydantic_object=QuizQuestion),
            "prompt": read_text_file("prompt/quizzify-prompt.txt"),
            "vectorstore_class": Chroma
        }
        
        self.file_type = file_type
        self.prompt = prompt or default_config["prompt"]
        self.model = model or default_config["model"]
        self.parser = parser or default_config["parser"]
        self.embedding_model = embedding_model or default_config["embedding_model"]
        
        self.vectorstore_class = vectorstore_class or default_config["vectorstore_class"]
        self.vectorstore, self.retriever, self.runner = None, None, None
        self.topic = topic
        self.lang = lang
        self.verbose = verbose
        
        if vectorstore_class is None: raise ValueError("Vectorstore must be provided")
        if topic is None: raise ValueError("Topic must be provided")
    
    def compile(self, documents: List[Document]):
        # Return the chain
        if self.file_type in ["csv", "xml", "xls", "xlsx", "json"]:
            cot_response = self.cot_structured(documents)
            documents = [Document(page_content=cot_response)]
            # documents = self.cot_structured(documents)  # Ensure this returns `Document` objects

        prompt = PromptTemplate(
            template=self.prompt,
            input_variables=["attribute_collection"],
            partial_variables={"format_instructions": self.parser.get_format_instructions()}
        )

        if self.runner is None:
            logger.info(f"Creating vectorstore from {len(documents)} documents") if self.verbose else None
            self.vectorstore = self.vectorstore_class.from_documents(documents, self.embedding_model)
            logger.info(f"Vectorstore created") if self.verbose else None

            self.retriever = self.vectorstore.as_retriever()
            logger.info(f"Retriever created successfully") if self.verbose else None

            self.runner = RunnableParallel(
                {"context": self.retriever, 
                "attribute_collection": RunnablePassthrough()
                }
            )
        
        chain = self.runner | prompt | self.model | self.parser
        
        if self.verbose: logger.info(f"Chain compilation complete")
        
        return chain
    
    def cot_structured(self, documents: List[Document]) -> str:
        # prompt = read_text_file("prompt/cot-prompt.txt")
        structured_data = "\n".join(doc.page_content for doc in documents)
        logger.info("****STRUCTURED DATA****: " + structured_data)
        prompt = f"""
        You are an expert in understanding various structured data formats such as CSV, XML, XLS, XLSX, and JSON. Your task is to perform a detailed analysis of the provided data to gain a comprehensive understanding of its structure and content. This understanding is crucial for accurately generating quiz questions based on this data.

        Follow these steps to analyze the data:

        1. **Identify the Format:**
        - Determine the format of the data (CSV, XML, XLS, XLSX, JSON). This will help in understanding the specific characteristics and structure associated with this format.

        2. **Examine the Structure:**
        - Analyze the data to identify its key components:
            - For CSV: Columns, headers, and rows.
            - For XML: Tags, attributes, and hierarchical structure.
            - For XLS/XLSX: Sheets, rows, columns, and cell content.
            - For JSON: Keys, values, nested objects, and arrays.

        3. **Describe Relationships:**
        - Identify and describe relationships between the components:
            - Are there hierarchical structures (e.g., parent-child relationships in XML)?
            - Are there key-value pairs (e.g., JSON objects)?
            - Are there tabular relationships (e.g., rows and columns in CSV/XLS)?

        4. **Identify Key Attributes and Patterns:**
        - Look for important attributes or patterns:
            - Numerical patterns, categorical fields, or text descriptions.
            - Common fields or recurring values that might be significant.

        5. **Infer the Purpose:**
        - Make logical inferences about the data’s purpose:
            - What might the data be used for? 
            - What is the subject matter or context?
            - How are the pieces of information connected?

        6. **Summarize the Data:**
        - Provide a summary of your findings:
            - A coherent interpretation of the data’s overall meaning.
            - Key components, relationships, attributes, and inferred purpose.

        **Data:**
        {structured_data}

        Your response should reflect a thorough understanding of the data's structure and content, helping to ensure accurate quiz generation based on this information.
        """
        response = self.model(prompt) # + could also include the structured_data here
        # Process the response and convert it to a list of Document objects
        if response:
            # documents = [Document(page_content=r) for r in response.split('\n')]
            # logger.info(f"COT response processed into {len(documents)} documents")
            logger.info("****RESPONSE****: " + response)
            # logger.info("****DOCUMENTS: " + str(documents))
        return response

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
    
    def create_questions(self, documents: List[Document], num_questions: int = 5) -> List[Dict]:
        if self.verbose: logger.info(f"Creating {num_questions} questions")
        
        if num_questions > 10:
            return {"message": "error", "data": "Number of questions cannot exceed 10"}
        
        chain = self.compile(documents)
        
        generated_questions = []
        attempts = 0
        max_attempts = num_questions * 5  # Allow for more attempts to generate questions

        while len(generated_questions) < num_questions and attempts < max_attempts:
            response = chain.invoke(f"Topic: {self.topic}, Lang: {self.lang}")
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

