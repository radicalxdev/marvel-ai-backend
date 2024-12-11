import os
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import List, TypedDict, Any
from langgraph.graph import StateGraph
from langgraph.graph import END
from pydantic import BaseModel, Field
from app.services.schemas import ChatMessage
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate

chat_google_genai = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)

def read_text_file(file_path):
    # Get the directory containing the script file
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Combine the script directory with the relative file path
    absolute_file_path = os.path.join(script_dir, file_path)
    
    with open(absolute_file_path, 'r') as file:
        return file.read()

class GraphState(TypedDict):
    user_query: str
    action: str
    chat_history: list[ChatMessage]

    result: Any

workflow = StateGraph(GraphState)

def process_content(
    state
):
    """ Tool for processing content """

    chat_history = " For context, you can use the chat history provided: " + " ".join(
        f"[{message.role} - {message.type}]: {message.text}" for message in state["chat_history"]
    )
    co_teacher_context = read_text_file('prompt/co_teacher_context.txt')

    action_map = {
        "translate": lambda: [
            ("system", co_teacher_context+read_text_file('../../../utils/actions_for_assistants/translate.txt')), 
            ("human", state["user_query"]+chat_history)
        ],
        "summarize": lambda: [
            ("system", co_teacher_context+read_text_file('../../../utils/actions_for_assistants/summarize.txt')),  
            ("human", state["user_query"]+chat_history)
        ],
        "rewrite": lambda: [
            ("system", co_teacher_context+read_text_file('../../../utils/actions_for_assistants/rewrite.txt')),  
            ("human", state["user_query"]+chat_history)
        ],
        "question_generation": lambda: [
            ("system", co_teacher_context+read_text_file('../../../utils/actions_for_assistants/question_generation.txt')),  
            ("human", state["user_query"]+chat_history)
        ],
        "custom": lambda: [
            ("system", co_teacher_context+read_text_file('../../../utils/actions_for_assistants/custom_prompt.txt')),  
            ("human", state["user_query"]+chat_history)
        ],
        "default": lambda: [
            ("system", co_teacher_context),  
            ("human", state["user_query"]+chat_history)
        ],
    }

    messages = action_map[state["action"]]()
    response = chat_google_genai.invoke(messages)
    return {
        "result": response.content
    }

def generate_questions_to_json(state):
    parser = JsonOutputParser(pydantic_object=QuestionList)
    prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            read_text_file('../../../utils/actions_for_assistants/system_prompt_question_generation_json.txt')
        ),
        ("human", read_text_file('../../../utils/actions_for_assistants/user_prompt_question_generation_json.txt'))
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
    if state['action'] == 'question_generation':
        return 'generate_questions_to_json'
    else:
        return END

workflow.add_node("process_content", process_content)
workflow.add_node("generate_questions_to_json", generate_questions_to_json)
workflow.set_entry_point("process_content")
workflow.add_conditional_edges(
    "process_content",
    go_to_process_questions_json,
    {
        'generate_questions_to_json': 'generate_questions_to_json',
        END: END
    }
)

def compile_co_teacher():
    app = workflow.compile()
    return app

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