from app.services.logger import setup_logger
from langchain_google_genai import GoogleGenerativeAI
from langchain_core.output_parsers import JsonOutputParser
import os
from langchain_core.prompts import PromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from typing import List

from fastapi import HTTPException


logger = setup_logger()

def read_text_file(file_path):
    # Get the directory containing the script file
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Combine the script directory with the relative file path
    absolute_file_path = os.path.join(script_dir, file_path)
    
    with open(absolute_file_path, 'r') as file:
        return file.read()

class CourseTypeGenerator:
    def __init__(self, prompt=None, model=None, parser=None, verbose:bool=False):
        default_config = {
            "model": GoogleGenerativeAI(model="gemini-1.5-pro"),
            "parser": JsonOutputParser(pydantic_object=CourseTypeSchema),
            "prompt": read_text_file("prompts/generate-topic-prompt.txt")
        }

        self.prompt = prompt or default_config["prompt"]
        self.model = model or default_config["model"]
        self.parser = parser or default_config["parser"]
        self.verbose = verbose

    def compile(self):
        # Return the chain
        prompt = PromptTemplate(
            template=self.prompt,
            input_variables=["topic"],
            partial_variables={"format_instructions": self.parser.get_format_instructions()}
        )

        chain = prompt | self.model | self.parser
        
        if self.verbose: logger.info(f"Chain compilation complete")
        
        return chain
        

class CourseTypeSchema(BaseModel):
    course_type: str = Field(description=""" The course type of a specific topic. It must be exactly only one of the following:
    - Language and Literature
    - Language Acquisition
    - Individuals and Societies
    - Sciences
    - Mathematics
    - Arts
    """)

def generate_course_type(topic: str=None, verbose: bool=False):
    try:
        course_type_generator = CourseTypeGenerator(verbose=verbose)
        chain = course_type_generator.compile()
        output = chain.invoke({"topic": topic})
    except Exception as e:
        logger.error(f"Failed to generate Worksheet: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate course type from LLM")

    return output

#Fill-in-the-blank question type
class QuestionBlank(BaseModel):
    key: str = Field(description="A unique identifier for the blank, starting from 0.")
    value: str = Field(description="The text content to fill in the blank")

class FillInTheBlankQuestion(BaseModel):
    question: str = Field(description="The question text with blanks indicated by placeholders (e.g., {0}, {1}, {2}, {3}, {4})")
    blanks: List[QuestionBlank] = Field(description="A list of blanks for the question, each with a key and a value")
    word_bank: List[str] = Field(description="A list of the correct texts that fill in the blanks, in random order")
    explanation: str = Field(description="An explanation of why the answers are correct")

    model_config = {
        "json_schema_extra": {
            "examples": """ 
                {
                "question": "The {0} of France is {1}, and it is known for its {2} and {3} {4}.",
                "blanks": [
                    {"key": "0", "value": "capital"},
                    {"key": "1", "value": "Paris"},
                    {"key": "2", "value": "art"},
                    {"key": "3", "value": "culinary"},
                    {"key": "4", "value": "delights"}
                ],
                "word_bank": ["delights", "art", "Paris", "culinary", "capital"],
                "explanation": "Paris is the capital of France, and it is renowned for its contributions to art and its exceptional culinary scene."
              }
          """
        }
    }

#Open-ended question type
class OpenEndedQuestion(BaseModel):
    question: str = Field(description="The open-ended question text")
    answer: str = Field(description="The expected correct answer")
    feedback: List[str] = Field(description="A list of possible answers for the provided question")

    model_config = {
        "json_schema_extra": {
            "examples": """ 
                {
                "question": "What is the significance of Paris in French history?",
                "answer": "Paris is the capital of France and has been a major center for politics, culture, art, and history.",
                "feedback": [
                    "Paris is the capital of France.",
                    "Paris has been a cultural center in Europe.",
                    "Paris played a major role in the French Revolution."
                ]
              }
          """
        }
    }

#True-False question type
class TrueFalseQuestion(BaseModel):
    question: str = Field(description="The True-False question text")
    answer: bool = Field(description="The correct answer, either True or False")
    explanation: str = Field(description="An explanation of why the answer is correct")

    model_config = {
        "json_schema_extra": {
            "examples": """ 
                {
                "question": "The Eiffel Tower is located in Paris.",
                "answer": true,
                "explanation": "The Eiffel Tower is a famous landmark located in Paris, France."
              }
          """
        }
    }

#Multiple Choice question type
class QuestionChoice(BaseModel):
    key: str = Field(description="A unique identifier for the choice using letters A, B, C, or D.")
    value: str = Field(description="The text content of the choice")
class MultipleChoiceQuestion(BaseModel):
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

#Relate concepts question type
class TermMeaningPair(BaseModel):
    term: str = Field(description="The term to be matched")
    meaning: str = Field(description="The meaning of the term")

class RelateConceptsQuestion(BaseModel):
    question: str = Field(description="The 'Relate concepts' question text")
    pairs: List[TermMeaningPair] = Field(description="A list of term-meaning pairs in disorder")
    answer: List[TermMeaningPair] = Field(description="A list of the correct term-meaning pairs in order")
    explanation: str = Field(description="An explanation of the correct term-meaning pairs")

    model_config = {
        "json_schema_extra": {
            "examples": """ 
                {
                "question": "Match each term with its correct meaning.",
                "pairs": [
                    {
                        "term": "Chlorophyll",
                        "meaning": "The powerhouse of the cell, where respiration and energy production occur."
                    },
                    {
                        "term": "Photosynthesis",
                        "meaning": "A green pigment responsible for the absorption of light to provide energy for photosynthesis."
                    },
                    {
                        "term": "Mitochondria",
                        "meaning": "The process by which green plants use sunlight to synthesize foods with the help of chlorophyll."
                    },
                    {
                        "term": "Nucleus",
                        "meaning": "The gel-like substance inside the cell membrane."
                    },
                    {
                        "term": "Cytoplasm",
                        "meaning": "The control center of the cell that contains DNA."
                    }
                ],
                "answer": [
                    {
                        "term": "Photosynthesis",
                        "meaning": "The process by which green plants use sunlight to synthesize foods with the help of chlorophyll."
                    },
                    {
                        "term": "Chlorophyll",
                        "meaning": "A green pigment responsible for the absorption of light to provide energy for photosynthesis."
                    },
                    {
                        "term": "Mitochondria",
                        "meaning": "The powerhouse of the cell, where respiration and energy production occur."
                    },
                    {
                        "term": "Nucleus",
                        "meaning": "The control center of the cell that contains DNA."
                    },
                    {
                        "term": "Cytoplasm",
                        "meaning": "The gel-like substance inside the cell membrane."
                    }
                ],
                "explanation": "Photosynthesis involves using sunlight to create food in plants, facilitated by chlorophyll. Mitochondria are involved in energy production in cells. The nucleus is the control center of the cell, and the cytoplasm is the gel-like substance within the cell membrane."
              }
          """
        }
    }

#Math. Exercise question type
class MathExerciseQuestion(BaseModel):
    question: str = Field(description="The math exercise question text")
    solution: str = Field(description="The step-by-step solution to the math problem")
    correct_answer: str = Field(description="The correct answer to the math problem")
    explanation: str = Field(description="An explanation of why the solution is correct")

    model_config = {
        "json_schema_extra": {
            "examples": """ 
                {
                "question": "Solve the equation: 2x + 3 = 11",
                "solution": "Step 1: Subtract 3 from both sides to get 2x = 8. Step 2: Divide both sides by 2 to get x = 4.",
                "correct_answer": "4",
                "explanation": "By isolating the variable x, we find that x equals 4."
              }
          """
        }
    }
