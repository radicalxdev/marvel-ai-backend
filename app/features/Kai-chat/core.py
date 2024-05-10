from langchain.llms import LLM
from langchain.memory.types.conversation_buffer import ConversationBufferMemory

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

def generate_prompt(message, conversation_history):
  """
  Creates a prompt considering user message, conversation history, and KAI introduction.
  """
  prompt = f"**Educator:** {message}\n"
  prompt += "**Conversation History:**\n"
  for msg in conversation_history:
    prompt += f"- {msg['input']}\n"
  prompt += """**KAI:** I'm your AI assistant for educational tasks. How can I help you today? 
  I can assist with best practices in teaching, management strategies, gamification techniques, course outlines, and more."
  """
  return prompt

def generate_response(llm: LLM, prompt):
  """
  Sends a prompt considering educator context and processes the LLM response.
  """
  response = llm.generate_text(prompt)
  return response.text

def get_conversation_history(user_id, user_buffers):
  """
  Retrieves conversation history for a specific user ID from the conversation memory buffer.
  """
  # Access conversation buffer for the user
  conversation_buffer = user_buffers.get(user_id)
  if not conversation_buffer:
    conversation_buffer = UserConversationBuffer()
    user_buffers[user_id] = conversation_buffer

  # Set the user ID for the conversation buffer object
  conversation_buffer.set_user_id(user_id)

  # Add the current message to the user's conversation history (assuming message is passed as a parameter elsewhere)
  # conversation_buffer.add_message(message)  # Uncomment if message is available here

  # Retrieve conversation history from the user's buffer
  user_history = conversation_buffer.get_history()
  return user_history
