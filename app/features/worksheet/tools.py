from typing import List, Tuple, Dict, Any


import os
import json
import time



from langchain_google_vertexai import VertexAI
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field

from services.logger import setup_logger
from services.tool_registry import ToolFile
from api.error_utilities import LoaderError

relative_path = "features/quzzify"

logger = setup_logger(__name__)

def read_text_file(file_path):
    # Get the directory containing the script file
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Combine the script directory with the relative file path
    absolute_file_path = os.path.join(script_dir, file_path)
    
    with open(absolute_file_path, 'r') as file:
        return file.read()


class WorksheetBuilder:
    def __init__(self, topic, grade_level, prompt_summary=None, prompt_multiple_choice=None, model=None, parser_multiple_choice=None, verbose=False):
        if topic is None or grade_level is None:
            raise ValueError("Topic and Grade level must be provided")
        
        default_config = {
            "model": VertexAI(model="gemini-1.0-pro", temperature = 0.3),
            "parser_multiple_choice": JsonOutputParser(pydantic_object=QuizQuestion),
            "prompt_summary": read_text_file("prompts/worksheet_prompt_summary.txt"),
            "prompt_multiple_choice": read_text_file("prompts/worksheet_prompt_multiple_choice.txt")
        }
        
        self.prompt_summary = prompt_summary or default_config["prompt_summary"]
        self.prompt_multiple_choice = prompt_multiple_choice or default_config["prompt_multiple_choice"]
        self.model = model or default_config["model"]
        self.parser_multiple_choice = parser_multiple_choice or default_config["parser_multiple_choice"]
        
        self.topic = topic
        self.grade_level = grade_level
        self.verbose = verbose
    
    def validate_and_format_multiple_choice_response(self, response) -> Tuple[bool, Dict]:
        try:
            if isinstance(response, dict):
                if 'question' in response and 'choices' in response:
                    choices = response['choices']
                    if isinstance(choices, dict):
                        # Format choices if they are in dict format
                        response['choices'] = self.format_choices(choices)
                    elif isinstance(choices, list):
                        # Check if choices are already formatted correctly
                        for choice in choices:
                            if not isinstance(choice, dict) or 'key' not in choice or 'value' not in choice:
                                return False, {}
                    else:
                        return False, {}
                    return True, response
            return False, {}
        except TypeError as e:
            if self.verbose:
                logger.error(f"TypeError during response validation: {e}")
            return False, {}

    def format_choices(self, choices: Dict[str, str]) -> List[Dict[str, str]]:
        return [{"key": k, "value": v} for k, v in choices.items()]
    
    def mcq_to_string(self, mcq_dict):
        mcq_string = ''
        mcq_string += mcq_dict['question'] + '\n'
        choices = mcq_dict['choices']
        for c in choices:
            mcq_string += c['key'] + ': ' + c['value'] + '\n'
        return mcq_string

    def create_multiple_choice(self, num_multiple_choice) -> str:
        # Return the chain
        prompt = PromptTemplate(
            template=self.prompt_multiple_choice,
            input_variables=["topic", "grade_level"],
            partial_variables={"format_instructions": self.parser_multiple_choice.get_format_instructions()}
        )
        
        chain = prompt | self.model | self.parser_multiple_choice
        
        if self.verbose: logger.info(f"Chain compilation complete")

        ### Create multiple choice here
        attempts = 0
        max_attempts = num_multiple_choice * 5  # Allow for more attempts to generate questions
        generated_questions = []

        while len(generated_questions) < num_multiple_choice and attempts < max_attempts:
            response = chain.invoke({"topic": self.topic, "grade_level": self.grade_level})
            
            if self.verbose:
                logger.info(f"Generated response attempt {attempts + 1}: {response}")
            
            # Directly check if the response format is valid
            flag, response = self.validate_and_format_multiple_choice_response(response)
            if flag:
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
            if len(generated_questions) < num_multiple_choice:
                logger.warning(f"Only generated {len(generated_questions)} out of {num_multiple_choice} requested questions")

            generated_questions = generated_questions[:num_multiple_choice]
            generated_questions_string = 'Multiple-Choice Questions\n'
            for i, gq in enumerate(generated_questions):
                generated_questions_string += 'MCQ ' + str(i + 1) + ':\n'
                mcq_string = self.mcq_to_string(gq)
                generated_questions_string += mcq_string + '\n'
            
        return generated_questions_string

    def create_worksheets(self, num_worksheets: int = 1, num_multiple_choice: int = 1) -> List[str]:
        if self.verbose: logger.info(f"Creating {num_multiple_choice} questions")
        
        if num_worksheets > 10:
            return {"message": "error", "data": "Number of questions cannot exceed 10"}
        
        
        generated_worksheets = []
        for i in range(num_worksheets):
            generated_multiple_choice = self.create_multiple_choice(num_multiple_choice)
            generated_worksheets.append(generated_multiple_choice)
        # Return the list of worksheets
        return generated_worksheets[:num_worksheets]

class QuestionChoice(BaseModel):
    key: str = Field(description="A unique identifier for the choice using letters A, B, C, D, etc.")
    value: str = Field(description="The text content of the choice")
class QuizQuestion(BaseModel):
    question: str = Field(description="The question text")
    choices: List[QuestionChoice] = Field(description="A list of choices")
    # answer: str = Field(description="The correct answer")
    # explanation: str = Field(description="An explanation of why the answer is correct")
