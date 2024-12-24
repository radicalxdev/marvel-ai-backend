
import os
from typing import List
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv, find_dotenv
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from langchain_core.runnables.base import RunnableLambda
from app.services.logger import setup_logger
from app.tools.utils.tool_utilities import (
    load_tool_metadata, 
    execute_tool, 
    finalize_inputs
)

from app.services.tool_registry import BaseTool

load_dotenv(find_dotenv())

logger = setup_logger()

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

marvel_ai_tools_prefix = "prompts/marvel_ai_tools/"

def adapt_marvel_tool_id(output, user_query, parser):
    return {
        "tool_id": output.strip(),
        "user_query": user_query,
        "request_sample": marvel_ai_tools_prefix+marvel_ai_tools_prompts[output.strip()],
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

def call_marvel_ai_tool(user_query: str):
    """Used for calling any of the following Marvel AI tools:
    1. Multiple Choice Quiz Generator
    2. Flashcards Generator
    3. Worksheet Generator
    4. Syllabus Generator
    5. AI-Resistant Assignments
    6. Connect with Them
    7. Presentation Generator
    8. Rubric Generator
    9. Lesson Plan Generator
    10. Writing Feedback Generator
    """
    prompt_identifier = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                read_text_file("prompts/system/generate_marvel_ai_tool_identifier.txt")
            ),
            (
                "human",
                read_text_file("prompts/human/generate_marvel_ai_tool_identifier.txt")
            )
        ]
    )

    chain_identifier = prompt_identifier | chat_google_genai
    
    prompt_generate_metadata = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                read_text_file("prompts/system/generate_marvel_ai_tool_metadata.txt")
            ),
            (
                "human",
                read_text_file("prompts/human/generate_marvel_ai_tool_metadata.txt")
            )
        ]
    )

    chain_generate_metadata = prompt_generate_metadata | chat_google_genai

    parser = JsonOutputParser(pydantic_object=ToolRequest)

    combined_chain = (
        chain_identifier
        | RunnableLambda(lambda x: adapt_marvel_tool_id(x.content, user_query, parser))
        | chain_generate_metadata
        | parser
    )

    result = combined_chain.invoke(user_query)

    logger.info(f"Metadata generated: {result}")

    result_with_schema = ToolRequest.model_validate(result)

    request_data = result_with_schema.tool_data    
    requested_tool = load_tool_metadata(request_data.tool_id)
    request_inputs_dict = finalize_inputs(request_data.inputs, requested_tool["inputs"])
    final_result = execute_tool(request_data.tool_id, request_inputs_dict)

    return final_result

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

class ToolRequest(BaseModel):
    tool_data: BaseTool

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

marvel_ai_tools_prompts = {
    "ai-resistant-assignments-generator": "ai_resistant_assignments_generator_request_sample.txt",
    "connect-with-them": "connect_with_them_request_sample.txt",
    "flashcard-generator": "flashcards_generator_request_sample.txt",
    "lesson-generator": "lesson_plan_generator_request_sample.txt",
    "multiple-choice-quiz-generator": "multiple_choice_quiz_generator_request_sample.txt",
    "presentation-generator": "presentation_generator_request_sample.txt",
    "rubric-generator": "rubric_generator_request_sample.txt",
    "syllabus-generator": "syllabus_generator_request_sample.txt",
    "worksheet-generator": "worksheet_generator_request_sample.txt",
    "writing-feedback-generator": "writing_feedback_generator_request_sample.txt",
}