from langchain_google_genai import ChatGoogleGenerativeAI
from typing import TypedDict, Any
from langgraph.graph import StateGraph
from langgraph.graph import END
from app.services.schemas import ChatMessage
import os
from dotenv import load_dotenv, find_dotenv

from app.utils.actions_for_assistants.actions_for_assistants import (
    generate_questions_to_json, 
    go_to_process_questions_json, 
    process_content
)
load_dotenv(find_dotenv())

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
    assistant_system_message: str

    result: Any

workflow = StateGraph(GraphState)

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