from langchain_google_vertexai import VertexAI
from langchain_core.output_parsers import JsonOutputParser

from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_core.prompts import PromptTemplate
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from services.logger import setup_logger
from pydantic import BaseModel, Field
import os

logger = setup_logger(__name__)

# AI Model
model = VertexAI(model="gemini-1.0-pro")

def read_text_file(file_path):
    # Get the directory containing the script file
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Combine the script directory with the relative file path
    absolute_file_path = os.path.join(script_dir, file_path)
    
    with open(absolute_file_path, 'r') as file:
        texts = file.read()

    # Split the text by '***'
    texts = texts.split('***')
    
    # Strip whitespace from each part and filter out empty strings
    texts = [text.strip() for text in texts if text.strip()]

    return texts

def concat_responses(responses):
       feedbacks = "\n\n".join(f"Feedback {index + 1}:\n{value}" for index, value in enumerate(responses))
       return {"feedbacks": feedbacks}


def get_feedback(solution, submission):
    aspects_path = "prompt/aspects.txt"
    aspects = read_text_file(aspects_path)

    prompts_path = "prompt/code_check-prompt.txt"
    prompts = read_text_file(prompts_path)
    system_message = prompts[0]
    human_message = prompts[1]
    summary_message = prompts[2]

    prompt_1 = ChatPromptTemplate.from_messages(
            [
            ("system", system_message),
            ("human", human_message),
            ]
        )

    prompt_1 = prompt_1.partial(solution = solution, submission = submission)

    output_parser = StrOutputParser()
    chain = RunnableParallel(aspect = RunnablePassthrough()) | prompt_1 | model | output_parser
    batch_inputs = [{"aspect": aspect} for aspect in aspects]
    
    responses = chain.batch(batch_inputs)

    prompt_2 = ChatPromptTemplate.from_messages(
       [
          ("system", summary_message),
       ]
    )
    chain = prompt_2 | model | output_parser
    feedback = chain.invoke(concat_responses(responses))
    
    return feedback