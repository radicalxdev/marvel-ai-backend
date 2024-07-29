from typing import List, Tuple, Dict, Any
import os

from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.output_parsers import JsonOutputParser
from langchain_google_genai import GoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from abc import ABC, abstractmethod

from app.services.logger import setup_logger

relative_path = "features/worksheet_generator"

logger = setup_logger(__name__)

def read_text_file(file_path):
    # Get the directory containing the script file
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Combine the script directory with the relative file path
    absolute_file_path = os.path.join(script_dir, file_path)
    
    with open(absolute_file_path, 'r') as file:
        return file.read()

# Class for the worksheet generation functionality
class WorksheetGenerator:
    def __init__(self, grade_level, topic, difficulty_level, question_types, prompt=None, model=None, parser=None, verbose=False):
        self.grade_level = grade_level
        self.topic = topic
        self.difficulty_level = difficulty_level
        self.question_types = question_types
        self.verbose = verbose
        
        if grade_level is None: raise ValueError("Grade level must be provided")
        if topic is None: raise ValueError("Topic must be provided")
        if difficulty_level is None: raise ValueError("Difficulty level must be provided")
        if question_types is None: raise ValueError("At lease one question type must be provided")

    def create_worksheet(self):
        params = {"grade_level": self.grade_level, "topic": self.topic, "difficulty_level": self.difficulty_level, "verbose": self.verbose}

        worksheet = []

        for question_type in self.question_types:
            if self.verbose: logger.info(f"Generating {question_type['question_type']} questions")

            #generating the question list
            question_list = create_question_builder(question_type['question_type'], **params).create_questions(question_type['num_questions'])
            worksheet.append(question_list)

        # Return the generated worksheet(list of lists that include questions of each type requested)
        return worksheet

# Abstract class for the question building functionality
class QuestionBuilder(ABC):
    @abstractmethod
    def __init__(self):
        pass

    def generate_question(self):
        # Return the generated response
        prompt = PromptTemplate(
            template=self.prompt,
            input_variables=["grade_level", "topic", "difficulty_level"],
            partial_variables={"format_instructions": self.parser.get_format_instructions()}
        )

        # Generate the final prompt by filling in the variables
        filled_prompt = prompt.format(
            grade_level=self.grade_level,
            topic=self.topic,
            difficulty_level=self.difficulty_level,
        )

        if self.verbose:
            logger.info(f"Generated prompt: {filled_prompt}")

        # Generate the question using the Google Gemini model
        response = self.model.generate(prompts = [filled_prompt])

        if self.verbose: logger.info("Response generation complete")
    
        # Extract the generated text from the response
        output = response.generations[0][0].text.strip()

        # Parse the JSON response using the configured parser
        parsed_output = self.parser.parse(output)

        if self.verbose: logger.info(f"Response parsing complete using {self.parser}")

        return parsed_output
    
    @abstractmethod
    def validate_response(self, response: Dict):
        pass

    @abstractmethod
    def transform_json_dict(input_data: Dict) -> Dict:
        pass

    @abstractmethod
    def create_questions(self, num_questions: int) -> List[Dict]:
        pass

class MultiChoiceQuestionBuilder(QuestionBuilder):
    def __init__(self, grade_level, topic, difficulty_level, prompt=None, model=None, parser=None, verbose=False):
        default_config = {
            "model": GoogleGenerativeAI(model="gemini-1.0-pro"),
            "parser": JsonOutputParser(pydantic_object=MultiChoiceQuestion),
            "prompt": read_text_file("prompt/multiple-choice-question-builder-prompt.txt")
        }
        
        self.prompt = prompt or default_config["prompt"]
        self.model = model or default_config["model"]
        self.parser = parser or default_config["parser"]
        
        self.grade_level = grade_level
        self.topic = topic
        self.difficulty_level = difficulty_level
        self.verbose = verbose
        
        if grade_level is None: raise ValueError("Grade level must be provided")
        if topic is None: raise ValueError("Topic must be provided")
        if difficulty_level is None: raise ValueError("Difficulty level must be provided")

    def transform_json_dict(self, input_data: Dict) -> Dict:
        # Validate and parse the input data to ensure it matches the MultiChoiceQuestion schema
        quiz_question = MultiChoiceQuestion(**input_data)

        # Transform the choices list into a dictionary
        transformed_choices = {choice.key: choice.value for choice in quiz_question.choices}

        # Create the transformed structure
        transformed_data = {
            "question": quiz_question.question,
            "choices": transformed_choices,
            "answer": quiz_question.answer,
        }

        return transformed_data
    
    def validate_response(self, response: Dict) -> bool:
        try:
            # Assuming the response is already a dictionary
            if isinstance(response, dict):
                if 'question' in response and 'choices' in response and 'answer' in response:
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
        if self.verbose: logger.info(f"Generating {num_questions} questions")
        
        if num_questions > 10:
            return {"message": "error", "data": "Number of questions cannot exceed 10"}       
        
        generated_questions = []
        attempts = 0
        max_attempts = num_questions * 5  # Allow for more attempts to generate questions

        while len(generated_questions) < num_questions and attempts < max_attempts:
            #response = chain.invoke(self.topic)
            response = self.generate_question()

            if self.verbose:
                logger.info(f"Generated response attempt {attempts + 1}: {response}")

            if response is None:
                if self.verbose:
                    logger.warning(f"Invalid null response. Attempt {attempts + 1} of {max_attempts}")
                attempts += 1
                continue

            response = self.transform_json_dict(response)

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
        
        # Return the list of questions
        return generated_questions[:num_questions]
    
class FillInBlankQuestionBuilder(QuestionBuilder):
    def __init__(self, grade_level, topic, difficulty_level, prompt=None, model=None, parser=None, verbose=False):
        default_config = {
            "model": GoogleGenerativeAI(model="gemini-1.0-pro"),
            "parser": JsonOutputParser(pydantic_object=FillInBlankQuestion),
            "prompt": read_text_file("prompt/fill-in-blank-question-builder-prompt.txt")
        }
        
        self.prompt = prompt or default_config["prompt"]
        self.model = model or default_config["model"]
        self.parser = parser or default_config["parser"]
        
        self.grade_level = grade_level
        self.topic = topic
        self.difficulty_level = difficulty_level
        self.verbose = verbose
        
        if grade_level is None: raise ValueError("Grade level must be provided")
        if topic is None: raise ValueError("Topic must be provided")
        if difficulty_level is None: raise ValueError("Difficulty level must be provided")

    def transform_json_dict(self, input_data: Dict) -> Dict:
        # Validate and parse the input data to ensure it matches the FillInBlankQuestion schema
        quiz_question = FillInBlankQuestion(**input_data)

        # Create the transformed structure
        transformed_data = {
            "question": quiz_question.question,
            "answer": quiz_question.answer,
        }

        return transformed_data
    
    def validate_response(self, response: Dict) -> bool:
        try:
            # Assuming the response is already a dictionary
            if isinstance(response, dict):
                if 'question' in response and 'answer' in response:
                    return True
            return False
        except TypeError as e:
            if self.verbose:
                logger.error(f"TypeError during response validation: {e}")
            return False
    
    def create_questions(self, num_questions: int = 5) -> List[Dict]:
        if self.verbose: logger.info(f"Generating {num_questions} questions")
        
        if num_questions > 10:
            return {"message": "error", "data": "Number of questions cannot exceed 10"}       
        
        generated_questions = []
        attempts = 0
        max_attempts = num_questions * 5  # Allow for more attempts to generate questions

        while len(generated_questions) < num_questions and attempts < max_attempts:
            #response = chain.invoke(self.topic)
            response = self.generate_question()

            if self.verbose:
                logger.info(f"Generated response attempt {attempts + 1}: {response}")

            if response is None:
                if self.verbose:
                    logger.warning(f"Invalid null response. Attempt {attempts + 1} of {max_attempts}")
                attempts += 1
                continue

            #fix for the bug in Pydantic schema use, where the response contain properties key
            if (not 'properties' in response):
                response = self.transform_json_dict(response)

                # Directly check if the response format is valid
                if self.validate_response(response):
                    generated_questions.append(response)
                    if self.verbose:
                        logger.info(f"Valid question added: {response}")
                        logger.info(f"Total generated questions: {len(generated_questions)}")
                else:
                    if self.verbose:
                        logger.warning(f"Invalid response format. Attempt {attempts + 1} of {max_attempts}")
            else: 
                if self.verbose:
                    logger.warning(f"Invalid response format. Attempt {attempts + 1} of {max_attempts}")

            # Move to the next attempt regardless of success to ensure progress
            attempts += 1

        # Log if fewer questions are generated
        if len(generated_questions) < num_questions:
            logger.warning(f"Only generated {len(generated_questions)} out of {num_questions} requested questions")
        
        # Return the list of questions
        return generated_questions[:num_questions]
    
class OpenEndedQuestionBuilder(QuestionBuilder):
    def __init__(self, grade_level, topic, difficulty_level, prompt=None, model=None, parser=None, verbose=False):
        default_config = {
            "model": GoogleGenerativeAI(model="gemini-1.0-pro"),
            "parser": JsonOutputParser(pydantic_object=OpenEndedQuestion),
            "prompt": read_text_file("prompt/open-ended-question-builder-prompt.txt")
        }
        
        self.prompt = prompt or default_config["prompt"]
        self.model = model or default_config["model"]
        self.parser = parser or default_config["parser"]
        
        self.grade_level = grade_level
        self.topic = topic
        self.difficulty_level = difficulty_level
        self.verbose = verbose
        
        if grade_level is None: raise ValueError("Grade level must be provided")
        if topic is None: raise ValueError("Topic must be provided")
        if difficulty_level is None: raise ValueError("Difficulty level must be provided")

    def transform_json_dict(self, input_data: Dict) -> Dict:
        # Validate and parse the input data to ensure it matches the OpenEndedQuestion schema
        quiz_question = OpenEndedQuestion(**input_data)

        if self.verbose:
            logger.info(f"Question validated through schema class")

        # Create the transformed structure
        transformed_data = {
            "question": quiz_question.question,
            "answer": quiz_question.answer,
        }

        return transformed_data
    
    def validate_response(self, response: Dict) -> bool:
        try:
            # Assuming the response is already a dictionary
            if isinstance(response, dict):
                if 'question' in response and 'answer' in response:
                    return True
            return False
        except TypeError as e:
            if self.verbose:
                logger.error(f"TypeError during response validation: {e}")
            return False
    
    def create_questions(self, num_questions: int = 5) -> List[Dict]:
        if self.verbose: logger.info(f"Generating {num_questions} questions")
        
        if num_questions > 10:
            return {"message": "error", "data": "Number of questions cannot exceed 10"}       
        
        generated_questions = []
        attempts = 0
        max_attempts = num_questions * 5  # Allow for more attempts to generate questions

        while len(generated_questions) < num_questions and attempts < max_attempts:
            response = self.generate_question()

            if self.verbose:
                logger.info(f"Generated response attempt {attempts + 1}: {response}")

            if response is None:
                if self.verbose:
                    logger.warning(f"Invalid null response. Attempt {attempts + 1} of {max_attempts}")
                attempts += 1
                continue

            #fix for the bug in Pydantic schema use, where the response contain properties key
            if 'properties' in response:
                # question generation is sucessful
                if isinstance(response['properties']['model_config']['default']['json_schema_extra']['examples'], list):
                    response = response['properties']['model_config']['default']['json_schema_extra']['examples'][0]
                # question generation is unsuccessful
                else:
                    if self.verbose:
                        logger.warning(f"Invalid response format. Attempt {attempts + 1} of {max_attempts}")
                    attempts += 1
                    continue

            response = self.transform_json_dict(response)

            # Directly check if the response format is valid
            if self.validate_response(response):
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
        
        # Return the list of questions
        return generated_questions[:num_questions]

# Mapping of question types to their respective classes
question_builder_classes = {
    "multiple-choice": MultiChoiceQuestionBuilder,
    "fill-in-blank": FillInBlankQuestionBuilder,
    "open-end": OpenEndedQuestionBuilder,
}

def create_question_builder(question_type, **kwargs):
    question_builder_class = question_builder_classes.get(question_type.lower())
    if not question_builder_class:
        raise ValueError(f"Unknown question type: {question_type}")
    return question_builder_class(**kwargs)

class QuestionChoice(BaseModel):
    key: str = Field(description="A unique identifier for the choice using letters A, B, C, or D.")
    value: str = Field(description="The text content of the choice")

class MultiChoiceQuestion(BaseModel):
    question: str = Field(description="The question text")
    choices: List[QuestionChoice] = Field(description="A list of choices for the question, each with a key and a value")
    answer: str = Field(description="The key of the correct answer from the choices list")

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
              }
          """
        }
      }
    
class FillInBlankQuestion(BaseModel):
    question: str = Field(description="The question text with the blank to be filled")
    answer: str = Field(description="The correct answer to the fill-in-the-blank question")

    model_config = {
        "json_schema_extra": {
            "examples": """ 
                {
                "question": "The Capital of France is _.",
                "answer": "Paris"
                }
            """
        }
    }
        
class OpenEndedQuestion(BaseModel):
    question: str = Field(description="The open ended question text")
    answer: str = Field(description="The correct answer for the question")

    model_config = {
        "json_schema_extra": {
            "examples": """ 
                {
                "question": "What are the main causes of climate change, and how do they impact the environment?",
                "answer": "The main causes of climate change are the burning of fossil fuels and deforestation, which release large amounts of carbon dioxide and other greenhouse gases into the atmosphere. These activities lead to global warming, resulting in severe weather events, rising sea levels, and disruptions to ecosystems.",
                }
            """
        }
    }