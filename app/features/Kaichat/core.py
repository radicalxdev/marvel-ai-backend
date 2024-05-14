from langchain_google_vertexai import VertexAI
from langchain.prompts import PromptTemplate

def build_prompt():
    """
    Build the prompt for the model.
    """
    
    template = """
    You are Kai, you are a helpful AI assistant for teachers. You are here to provide guidance and support for educational strategies. The user's name is {user_name}. The user has asked the following question. Please answer succinctly and informatively. For context, you can use the chat history provided below. Do not answer questions outside of educational topics.
    
    User Query:
    ---------------------------------------
    {user_query}
    
    Chat History:
    ---------------------------------------
    {chat_history}
    """
    # Create system message for intro context to model    
    prompt = PromptTemplate(
        template = template,
        input_variables=['user_name', 'user_query', 'chat_history']
    )
    
    return prompt
    
    # Create human query message for model


def executor(user_name, user_query, messages):
    
    # create a memory list of last k = 3 messages
    chat_context = [message.payload.text for message in messages[-3:]]
    print(chat_context)

    prompt = build_prompt()
    
    llm = VertexAI(model_name="gemini-1.0-pro")
    
    from langchain_core.runnables import RunnableParallel, RunnablePassthrough
    
    runner = RunnableParallel(
        {"chat_history": RunnablePassthrough(), "user_name": RunnablePassthrough(), "user_query": RunnablePassthrough()},
    )
    
    chain = runner | prompt | llm
    
    response = chain.invoke({"chat_history": chat_context, "user_name": user_name, "user_query": user_query})
    
    return response
