import re
import os

from langchain_google_vertexai import VertexAI
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from services.logger import setup_logger
from langchain_core.pydantic_v1 import BaseModel, Field
from typing import List, Dict
from sentence_transformers import SentenceTransformer, util


relative_path = "features/worksheet_generator"

logger = setup_logger(__name__)


def read_text_file(file_path):
    # Get the directory containing the script file
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Combine the script directory with the relative file path
    absolute_file_path = os.path.join(script_dir, file_path)

    with open(absolute_file_path, 'r') as file:
        return file.read()
class WorksheetBuilder:
    def __init__(self, db, topic, level=None, hint=None, q_type=""):
        default_config = {
            "model": VertexAI(model="gemini-1.0-pro"),
            "parser": JsonOutputParser(pydantic_object=QuizQuestion),
            "prompt": read_text_file("prompt/worksheet-generator-quiz-prompt.txt")
        }
        self.prompt = {"quiz": default_config["prompt"],
                       "worksheet": read_text_file("prompt/worksheet-generator-worksheet-prompt.txt")}
        self.model = default_config['model']
        self.db = db
        self.topic = topic
        self.level = level
        self.q_type = q_type
        self.hint = hint
        self.verbose = True
        self.parser = {"quiz": default_config["parser"],"worksheet":JsonOutputParser(pydantic_object=WorksheetQuestion)}

        if db is None: raise ValueError("Vectorstore must be provided")
        if topic is None: raise ValueError("Topic must be provided")
        if level is None: raise ValueError("Level must be provided")

    def generate_prompt(self, topic, level, hint, parser, q_type):
        self.topic = topic.lower()
        self.level = level.lower()
        self.hint = hint.lower()
        self.q_type = q_type.lower()
        prompt_template = self.prompt[self.q_type]
        prompt = PromptTemplate(input_variables = ["topic","level","q_type","hint"], template = prompt_template,
                                partial_variables={"format_instructions": parser.get_format_instructions()})
        return prompt


    def execute(self):

        # if self.q_type == "quiz":
        prompt = self.generate_prompt(self.topic, self.level, self.hint, self.parser[self.q_type], self.q_type)
        #
        # if self.q_type == "worksheet":
        #     prompt = self.generate_prompt(self.topic, self.level, self.hint, self.parser[self.q_type], self.q_type)

        retriever = self.db.as_retriever()

        runner = RunnableParallel({"context": retriever, "topic":RunnablePassthrough(), "hint": RunnablePassthrough(),
                                   "q_type" : RunnablePassthrough(),
                                   "level":RunnablePassthrough()})
        print("--------------------------generated prompt--------------------", prompt)

        retrieval_chain_quiz = (runner | prompt | self.model | self.parser["quiz"])

        retrieval_chain_worksheet = (runner | prompt | self.model | self.parser["worksheet"])

        if self.verbose:
            print("Chain successfully created",retrieval_chain_quiz,retrieval_chain_worksheet)
        if self.q_type == "quiz": return retrieval_chain_quiz
        if self.q_type == "worksheet": return retrieval_chain_worksheet

    def validate_response(self, response: dict) -> bool:
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

    def validate_worksheet_response(self, response: dict) -> bool:
        try:
            # Assuming the response is already a dictionary
            if isinstance(response, dict):
                if 'question' in response and 'answer' in response and 'explanation' in response:
                        return True
            return False
        except TypeError as e:
            if self.verbose:
                logger.error(f"TypeError during response validation: {e}")
            return False

    def is_valid_dict_values(self, json_dict):
        """
        Check if the dictionary values contain special or newline characters.
        """
        for key, value in json_dict.items():
            if isinstance(value, str) and re.search(r'[\n\r]', value):
                return False
        return True

    def format_choices(self, choices: Dict[str, str]) -> List[Dict[str, str]]:
        return [{"key": k, "value": v} for k, v in choices.items()]

    def create_questions(self, num_questions: int = 5) -> dict[str, str] | list[str]:
        if self.verbose: logger.info(f"Creating {num_questions} questions")

        if num_questions > 10:
            return {"message": "error", "data": "Number of questions cannot exceed 10"}

        chain = self.execute()

        generated_questions = []
        attempts = 0
        max_attempts = num_questions * 5  # Allow for more attempts to generate questions
        print("len of gen qs", len(generated_questions))
        while len(generated_questions) < num_questions and attempts < max_attempts:
            response = chain.invoke(self.topic)
            if self.verbose:
                logger.info(f"Generated response attempt {attempts + 1}: {response}")

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

        if len(generated_questions) == 10:
            if self.verbose: logger.info(f"10 questions generated, Deleting vectorstore")
            self.db.delete_collection()

        # Return the list of questions
        return generated_questions[:num_questions]
    def validate_qtype_response(self, hint: str, answer) -> bool:
        if "single sentence" in hint:
            return 10 <= len(answer.split()) <= 400
        if "integer" in hint:
            try:
                int(answer)
                return True
            except ValueError:
                return False

    def is_response_relevant(self, response: dict) -> bool:
        model = SentenceTransformer('all-MiniLM-L6-v2')

        question = response['question']
        answer = response['answer']
        explanation = response['explanation']

        # Generate embeddings for question, answer, and explanation
        question_embedding = model.encode(question, convert_to_tensor=True)
        answer_embedding = model.encode(answer, convert_to_tensor=True)
        explanation_embedding = model.encode(explanation, convert_to_tensor=True)

        # Calculate cosine similarity
        question_answer_similarity = util.cos_sim(question_embedding, answer_embedding)
        question_explanation_similarity = util.cos_sim(question_embedding, explanation_embedding)

        # Convert tensor to scalar for easier interpretation
        question_answer_similarity = question_answer_similarity.item()
        question_explanation_similarity = question_explanation_similarity.item()

        print(f"Question: {question}")
        print(f"Answer: {answer}")
        print(f"Explanation: {explanation}")
        print(f"Similarity between question and answer: {question_answer_similarity:.4f}")
        print(f"Similarity between question and explanation: {question_explanation_similarity:.4f}")
        return max(question_answer_similarity, question_explanation_similarity)

    def create_worksheet_questions(self, hint_num=3):
        chain = self.execute()

        generated_questions = []
        attempts = 0
        max_attempts = hint_num * 5

        print("len of gen qs", len(generated_questions))
        while len(generated_questions) < hint_num and attempts < max_attempts:
            response = chain.invoke(self.topic)
            if self.verbose:
                logger.info(f"Generated response attempt {attempts + 1}: {response}")

            # Check for "choices" type and validate against instructions
            if "choices" in response or not self.is_valid_dict_values(response) or not self.validate_worksheet_response(response)\
                    or not self.validate_qtype_response(self.hint, response['answer']):
                logger.warning(
                        f"Question is choices type and doesn't meet instructions. Attempt {attempts + 1} of {max_attempts}")
                attempts += 1
                continue

            # Valid question, add to list
            if self.is_response_relevant(response) >= 0.6:
                generated_questions.append(response)
            if self.verbose:
                logger.info(f"Valid question added: {response}")
                logger.info(f"Total generated questions: {len(generated_questions)}")

        # Log if fewer questions are generated
        if len(generated_questions) < hint_num:
            logger.warning(f"Only generated {len(generated_questions)} out of {hint_num} requested questions")

        if self.verbose:
            logger.info(f"Deleting vectorstore")
        self.db.delete_collection()

        # Return the list of questions
        return generated_questions[:hint_num]


class QuestionChoice(BaseModel):
    key: str = Field(description="A unique identifier for the choice using letters A, B, C, D, etc.")
    value: str = Field(description="The text content of the choice")

class QuizQuestion(BaseModel):
    question: str = Field(description="The question text")
    choices: List[QuestionChoice] = Field(description="A list of choices")
    answer: str = Field(description="The correct answer")
    explanation: str = Field(description="An explanation of why the answer is correct")
    
class WorksheetQuestion(BaseModel):
    question: str = Field(description="The question text")
    answer: str = Field(description="The correct answer")
    explanation: str = Field(default="", description="An explanation of why the answer is correct")






