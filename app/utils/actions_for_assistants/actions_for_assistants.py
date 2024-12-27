
import os
from typing import List
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv, find_dotenv
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import END
from pydantic import BaseModel, Field

load_dotenv(find_dotenv())

chat_google_genai = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)

def read_text_file(file_path):
    # Get the directory containing the script file
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Combine the script directory with the relative file path
    absolute_file_path = os.path.join(script_dir, file_path)
    
    with open(absolute_file_path, 'r') as file:
        return file.read()

def process_content(
    state
):
    """
    This function, `process_content`, is designed to dynamically generate a response based on the user's action and context. 
    It takes in a `state` dictionary that contains information such as the user's query, the intended action (e.g., translate, 
    summarize, rewrite, generate questions, or a custom task), and chat history for added context.

    The function performs the following steps:
    1. Constructs the chat history string to provide context for processing.
    2. Maps specific actions to corresponding prompt templates and logic using `action_map`.
    3. Invokes a generative AI model (`chat_google_genai`) with the appropriate system and user messages based on the action selected.
    4. Returns the processed result as a response.

    Each action retrieves a predefined template from corresponding prompt files and appends the user query and chat history for 
    contextualized processing. If an invalid action is passed, the function raises an error.
    """

    chat_history = " For context, you can use the chat history provided: " + " ".join(
        f"[{message.role} - {message.type}]: {message.text}" for message in state["chat_history"]
    )

    action_map = {
        "translate": lambda: [
            ("system", state["assistant_system_message"]+read_text_file('prompts/translate.txt')), 
            ("human", state["user_query"]+chat_history)
        ],
        "summarize": lambda: [
            ("system", state["assistant_system_message"]+read_text_file('prompts/summarize.txt')),  
            ("human", state["user_query"]+chat_history)
        ],
        "rewrite": lambda: [
            ("system", state["assistant_system_message"]+read_text_file('prompts/rewrite.txt')),  
            ("human", state["user_query"]+chat_history)
        ],
        "question_generation": lambda: [
            ("system", state["assistant_system_message"]+read_text_file('prompts/question_generation.txt')),  
            ("human", state["user_query"]+chat_history)
        ],
        "custom": lambda: [
            ("system", state["assistant_system_message"]+read_text_file('prompts/custom_prompt.txt')),  
            ("human", state["user_query"]+chat_history)
        ],
        "default": lambda: [
            ("system", state["assistant_system_message"]),  
            ("human", state["user_query"]+chat_history)
        ],
    }

    if state["action"] not in action_map:
        raise ValueError(f"Action '{state['action']}' is not a valid action in the action_map")

    messages = action_map[state["action"]]()
    response = chat_google_genai.invoke(messages)
    return {
        "result": response.content
    }

def generate_questions_to_json(state):
    """
    The function `generate_questions_to_json` is designed to transform a list of questions into a structured JSON format. 
    It utilizes a predefined parsing schema and a generative AI chain to process the input and produce the desired output.

    Key steps in the function:
    1. Parser Setup: Initializes a `JsonOutputParser` using the `QuestionList` schema to define the expected JSON structure.
    2. Prompt Definition: Loads system and user prompt templates from external files (`prompts/system_prompt_question_generation_json.txt` 
    and `prompts/user_prompt_question_generation_json.txt`) to provide instructions and context for generating the JSON.
    3. AI Chain Setup: Combines the prompt and generative AI model (`chat_google_genai`) into a processing chain.
    4. Invocation: Calls the chain with the questions (from `state["result"]`) and format instructions provided by the parser, ensuring the 
    output adheres to the predefined JSON schema.
    5. Result Parsing: Parses the AI-generated content using the parser to ensure it matches the structured format.

    The function returns a dictionary containing the `result`, which is the parsed JSON object representing the list of questions in 
    a structured format.
    """
    parser = JsonOutputParser(pydantic_object=QuestionList)
    prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            read_text_file('prompts/system_prompt_question_generation_json.txt')
        ),
        ("human", read_text_file('prompts/user_prompt_question_generation_json.txt'))
    ]
    )

    chain = prompt | chat_google_genai

    result = chain.invoke(
        {
            "questions": state["result"],
            "format_instructions": parser.get_format_instructions()
        }
    )
    
    return {
        "result": parser.parse(result.content)
    }
    

def go_to_process_questions_json(state):
    """
    Determines the next processing step based on the action in the `state`. 
    Returns `'generate_questions_to_json'` if the action is `'question_generation'`, otherwise returns `END`.
    """

    if state['action'] == 'question_generation':
        return 'generate_questions_to_json'
    else:
        return END

class QuestionChoice(BaseModel):
    key: str = Field(description="A unique identifier for the choice using letters A, B, C, or D.")
    value: str = Field(description="The text content of the choice")
class MultipleChoiceQuestion(BaseModel):
    question: str = Field(description="The question text")
    choices: List[QuestionChoice] = Field(description="A list of choices for the question, each with a key and a value")
    answer: str = Field(description="The key of the correct answer from the choices list")
    explanation: str = Field(description="An explanation of why the answer is correct")

class OpenEndedQuestion(BaseModel):
    question: str = Field(description="The open-ended question text")
    answer: str = Field(description="The expected correct answer")
    feedback: List[str] = Field(description="A list of possible answers for the provided question")

class QuestionList(BaseModel):
    multiple_choice_questions: List[MultipleChoiceQuestion]
    open_ended_questions: List[OpenEndedQuestion]