
import os
from typing import List
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv, find_dotenv
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from langchain_core.runnables.base import RunnableLambda

load_dotenv(find_dotenv())

chat_google_genai = ChatGoogleGenerativeAI(model="gemini-2.0-flash-exp", temperature=0)

def read_text_file(file_path):
    # Get the directory containing the script file
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Combine the script directory with the relative file path
    absolute_file_path = os.path.join(script_dir, file_path)
    
    with open(absolute_file_path, 'r') as file:
        return file.read()
    

def adapt_questions_for_json(output, parser):
    return {
        "questions": output,
        "format_instructions": parser.get_format_instructions()
    }

def translation_tool(user_query: str, source_lang: str, target_lang: str):
    """ Used for translating content from a source language to a target language. """
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                read_text_file("prompts/system/translation_tool.txt")
            ),
            (
                "human",
                read_text_file("prompts/human/translation_tool.txt")
            )
        ]
    )

    chain = prompt | chat_google_genai
    result = chain.invoke({
        "user_query": user_query,
        "source_lang": source_lang,
        "target_lang": target_lang
    })
    return result.content

def summarization_tool(user_query: str, summarization_type: str):
    """ Used for summarize content"""
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                read_text_file("prompts/system/summarization_tool.txt")
            ),
            (
                "human",
                read_text_file("prompts/human/summarization_tool.txt")
            )
        ]
    )

    chain = prompt | chat_google_genai
    result = chain.invoke({
        "user_query": user_query,
        "summarization_type": summarization_type
    })
    return result.content

def rewrite_tool(user_query: str, focus: str, tone: str):
    """ Used for rewriting content"""
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                read_text_file("prompts/system/rewrite_tool.txt")
            ),
            (
                "human",
                read_text_file("prompts/human/rewrite_tool.txt")
            )
        ]
    )

    chain = prompt | chat_google_genai
    result = chain.invoke({
        "user_query": user_query,
        "focus": focus,
        "tone": tone
    })
    return result.content

def custom_prompt_tool(user_query: str, action: str):
    """ Used for managing custom prompts"""
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                read_text_file("prompts/system/custom_prompt_tool.txt")
            ),
            (
                "human",
                read_text_file("prompts/human/custom_prompt_tool.txt")
            )
        ]
    )

    chain = prompt | chat_google_genai
    result = chain.invoke({
        "user_query": user_query,
        "action": action
    })
    return result.content


def generate_questions_to_json_tool(user_query: str):
    """ Used for generating questions. The results are returned in a JSON format. You must respect the user's language """
    prompt_generate_questions = ChatPromptTemplate.from_messages(
      [
          (
            "system",
            read_text_file("prompts/system/question_generation.txt")
          ),
          ("human",
            read_text_file("prompts/human/question_generation.txt")
          )
      ]
    )

    chain_generate_questions = prompt_generate_questions | chat_google_genai

    parser = JsonOutputParser(pydantic_object=QuestionList)
    prompt_questions_to_json = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            read_text_file("prompts/system/generate_questions_to_json_tool.txt")
        ),
        ("human",
            read_text_file("prompts/human/generate_questions_to_json_tool.txt")
        )
    ]
    )

    chain_questions_to_json = prompt_questions_to_json | chat_google_genai
    combined_chain = (
        chain_generate_questions
        | RunnableLambda(lambda x: adapt_questions_for_json(x.content, parser))
        | chain_questions_to_json
        | parser
    )

    result = combined_chain.invoke(user_query)

    return result

def default_prompt_tool(user_query: str):
    """Used for answering any kind of prompt that is not about Translation, Summarization,
    Rewriting, Question Generation, or Custom Prompts"""
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                read_text_file("prompts/system/default_prompt_tool.txt")
            ),
            (
                "human",
                read_text_file("prompts/human/default_prompt_tool.txt")
            )
        ]
    )

    chain = prompt | chat_google_genai
    result = chain.invoke({
        "user_query": user_query
    })
    return result.content

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

actions = [
    translation_tool,
    summarization_tool,
    rewrite_tool,
    generate_questions_to_json_tool,
    custom_prompt_tool,
    default_prompt_tool
]

function_map = {
    "translation_tool": translation_tool,
    "summarization_tool": summarization_tool,
    "rewrite_tool": rewrite_tool,
    "generate_questions_to_json_tool": generate_questions_to_json_tool,
    "custom_prompt_tool": custom_prompt_tool,
    "default_prompt_tool": default_prompt_tool
}