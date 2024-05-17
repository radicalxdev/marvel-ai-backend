from langchain_google_vertexai import VertexAI
from langchain.prompts import PromptTemplate, ChatPromptTemplate
from services.schemas import ChatMessage, Message
from services.logger import read_blob_to_string

def build_prompt():
    """
    Build the prompt for the model.
    """
    
    prompt_file_path = "prompt/kai-prompt.txt"  
    with open(prompt_file_path, "r") as f:
        template = f.read()

    prompt = PromptTemplate(
        template=template,
        input_variables=["text"],
    )
    
    return prompt


def executor(user_name: str, user_query: str, messages: list[Message], k=10):
    
    # create a memory list of last k = 3 messages
    chat_context = [
        ChatMessage(
            role=message.role, 
            type=message.type, 
            text=message.payload.text
        ) for message in messages[-k:]
    ]

    prompt = build_prompt()
    
    llm = VertexAI(model_name="gemini-1.0-pro")
    
    chain =  prompt | llm
    
    response = chain.invoke({"chat_history": chat_context, "user_name": user_name, "user_query": user_query})
    
    return response
