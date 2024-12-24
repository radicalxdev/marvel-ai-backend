import os
from dotenv import load_dotenv, find_dotenv
import google.generativeai as genai
from google.ai.generativelanguage_v1beta.types import content
from app.services.logger import setup_logger
from app.utils.actions_for_assistants.actions_for_assistants import (
    actions,
    function_map
)

load_dotenv(find_dotenv())

genai.configure(api_key=os.environ['GOOGLE_API_KEY'])

logger = setup_logger()

def read_text_file(file_path):
    # Get the directory containing the script file
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Combine the script directory with the relative file path
    absolute_file_path = os.path.join(script_dir, file_path)
    
    with open(absolute_file_path, 'r') as file:
        return file.read()

model = genai.GenerativeModel(model_name='gemini-2.0-flash-exp',
                              system_instruction=read_text_file('prompt/co_teacher_context.txt'),
                              tools=actions)

def run_co_teacher_assistant(user_query: str, chat_context: str, **kwargs):
  chat = model.start_chat()

  user_name = kwargs.get("user_name", "Unknown")
  user_age = kwargs.get("user_age", 0)
  user_preference = kwargs.get("user_preference", "None")

  response = chat.send_message(f"""
                               User query: {user_query}\n
                               Personalize the response for {user_name} (Age: {user_age}) with preference: {user_preference}.\n
                               You can use the chat context if further information is needed: {chat_context}\n
                               """)

  result = None

  while True:
      for part in response.parts:
          if fn := part.function_call:
              args = ", ".join(f"{key}={val}" for key, val in fn.args.items())
              logger.info(f"USING THE FUNCTION: {fn.name}({args})")
              break
      else:
          logger.info(f"FINAL RESPONSE: {response.text}")
          break

      fc = response.candidates[0].content.parts[0].function_call
      try:
        result = function_map[fc.name](**fc.args)
      except Exception as e:
        logger.error(e)
        
      logger.info(f"GENERATED RESULT: {result}")

      response = chat.send_message(
          genai.protos.Content(
              parts=[genai.protos.Part(
                  function_response=genai.protos.FunctionResponse(
                      name=fc.name,
                      response={'result': result}))]))

  return result, response.text