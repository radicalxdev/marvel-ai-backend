from langchain_google_vertexai import VertexAI
from langchain.prompts import PromptTemplate, ChatPromptTemplate
from services.schemas import ChatMessage, Message
from services.gcp import read_blob_to_string

def build_prompt():
    """
    Build the prompt for the model.
    """
    
    template = read_blob_to_string(bucket_name="backend-prompt-lib", file_path="kaichat/05142024-kaichat-prompt.txt")
    # Create system message for intro context to model    
    prompt = PromptTemplate(
        template = template,
        input_variables=['user_name', 'user_query', 'chat_history']
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
