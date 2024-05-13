from langchain_google_vertexai import VertexAI
from langchain.memory import ConversationBufferMemory
from .kai_prompt import join_prompt 

user_buffers = {}


class UserConversationBuffer:
    """
    Class to manage conversation history for a specific user ID within the memory buffer.
    """

    def __init__(self, max_length=100):
        self.buffer = ConversationBufferMemory(max_length=max_length)
        self.user_id = None

    def set_user_id(self, user_id):
        self.user_id = user_id

    def add_message(self, message):
        if self.user_id:
            self.buffer.add(message, input=message)

    def get_history(self):
        if self.user_id:
            return self.buffer.get_history()
        else:
            return []


def get_conversation_history(user_id, user_buffers):

    # Check if the user already has a conversation buffer initialized
    if user_id not in user_buffers:
        user_buffers[user_id] = UserConversationBuffer()

    conversation_buffer = user_buffers[user_id]
    conversation_buffer.set_user_id(user_id)  # Ensure this is set once during initialization

    return conversation_buffer.get_history()


def update_conversation_history(user_id, user_message, bot_response):
    if user_id not in user_buffers:
        user_buffers[user_id] = UserConversationBuffer()

    conversation_buffer = user_buffers[user_id]
    conversation_buffer.set_user_id(user_id)
    conversation_buffer.add_message({"input": user_message, "output": bot_response})


def generate_response(vertex_ai: VertexAI, user_id, user_name, user_query):
    conversation_history = get_conversation_history(user_id, user_buffers)
    chat_template = join_prompt(user_name, user_query, conversation_history)

    # Assuming you have a method to convert chat_template into a string prompt
    formatted_prompt = str(chat_template)  # Simplified for demonstration; adjust as needed

    response = vertex_ai.generate_text(formatted_prompt)
    update_conversation_history(user_id, user_query, response.text)

    return response.text


# Assuming we have a function to handle incoming requests
def handle_user_interaction(user_id, user_name, user_query):
    vertex_ai = VertexAI()  # Initialize VertexAI client
    response = generate_response(vertex_ai, user_id, user_name, user_query)
    print("Response to User:", response)


# Example call to handle interaction
handle_user_interaction("user123", "Alice", "How do I improve student engagement?")
