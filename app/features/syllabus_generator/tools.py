# This is code for quizzify repurpose for syllabus generator
### MINI FUNCTIONS FOR EAC SUB PART OF THE SYLLABUS AND THEN ONE FINAL FUNCTION TO COMBINE THE OUTPUT

from typing import List, Tuple, Dict, Any
from io import BytesIO
from fastapi import UploadFile
from pypdf import PdfReader
from urllib.parse import urlparse
import requests
import os
import json
import time

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_google_genai import GoogleGenerativeAI
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_google_genai import GoogleGenerativeAI

from app.services.logger import setup_logger
from app.services.tool_registry import ToolFile
from app.api.error_utilities import LoaderError

relative_path = "features/syllabus"

logger = setup_logger(__name__)

# All functions and procedures program requires should be in tools.py

def read_text_file(file_path):
    # Get the directory containing the script file
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Combine the script directory with the relative file path
    absolute_file_path = os.path.join(script_dir, file_path)
    with open(absolute_file_path, 'r') as file:
        return file.read()

def build_prompt(filepath):
    """
    Build the prompt for the model.
    """
    template = read_text_file(filepath)
    prompt = PromptTemplate.from_template(
        template)
    return prompt

def course_description(grade:str,subject:str,custom_info='None') -> str:
    #prompt = read_text_file('prompt/course_description.txt')
    #prompt = PromptTemplate.format(prompt)
    prompt = build_prompt('prompts/course_description.txt')
    #prompt.format({'grade':grade,'subject':subject})
    model = GoogleGenerativeAI(model="gemini-1.0-pro")
    chain = prompt | model
    response = chain.invoke({"grade":grade,"subject":subject,"custom_info":custom_info})
    return response

def course_objectives(grade:str,subject:str,course_description:str,custom_info='None') -> str:
    #prompt = read_text_file('prompt/course_description.txt')
    #prompt = PromptTemplate.format(prompt)
    prompt = build_prompt('prompts/course_objectives.txt')
    #prompt.format({'grade':grade,'subject':subject})
    model = GoogleGenerativeAI(model="gemini-1.0-pro")
    chain = prompt | model
    response = chain.invoke({"grade":grade,"subject":subject,"custom_info":custom_info,'course_description':course_description})
    return response

def course_outline(grade:str,subject:str,course_description:str,course_objectives:str,custom_info='None') -> str:
    #prompt = read_text_file('prompt/course_description.txt')
    #prompt = PromptTemplate.format(prompt)
    prompt = build_prompt('prompts/course_outline.txt')
    #prompt.format({'grade':grade,'subject':subject})
    model = GoogleGenerativeAI(model="gemini-1.0-pro")
    chain = prompt | model
    response = chain.invoke({"grade":grade,"subject":subject,"custom_info":custom_info,'course_description':course_description,
                             'course_objectives':course_objectives})
    return response

def grading_policy(grade:str,subject:str,course_outline:str,custom_info='None') -> str:
    #prompt = read_text_file('prompt/course_description.txt')
    #prompt = PromptTemplate.format(prompt)
    prompt = build_prompt('prompts/grading_policy.txt')
    #prompt.format({'grade':grade,'subject':subject})
    model = GoogleGenerativeAI(model="gemini-1.0-pro")
    chain = prompt | model
    response = chain.invoke({"grade":grade,"subject":subject,"custom_info":custom_info,'course_outline':course_outline})
    return response

def rules_policies(grade:str,subject:str,course_outline:str,custom_info='None') -> str:
    #prompt = read_text_file('prompt/course_description.txt')
    #prompt = PromptTemplate.format(prompt)
    prompt = build_prompt('prompts/rules_policies.txt')
    #prompt.format({'grade':grade,'subject':subject})
    model = GoogleGenerativeAI(model="gemini-1.0-pro")
    chain = prompt | model
    response = chain.invoke({"grade":grade,"subject":subject,"custom_info":custom_info,'course_outline':course_outline})
    return response

def study_materials(grade:str,subject:str,course_outline:str,custom_info='None') -> str:
    #prompt = read_text_file('prompt/course_description.txt')
    #prompt = PromptTemplate.format(prompt)
    prompt = build_prompt('prompts/study_materials.txt')
    #prompt.format({'grade':grade,'subject':subject})
    model = GoogleGenerativeAI(model="gemini-1.0-pro")
    chain = prompt | model
    response = chain.invoke({"grade":grade,"subject":subject,"custom_info":custom_info,'course_outline':course_outline})
    return response

def final_output(course_description:str,course_objectives:str,course_outline:str,grading_policy:str,rules_policies:str,study_materials:str) -> str:
    # response = f"#Course Description\n{course_description}\n\n#Course Objectives\n{course_objectives}\n\n" \
    # "#Course Outline\n{course_outline}\n\n#Grading Policy\n{grading_policy}\n\n" \
    # "#Class Rules\n{rules_policies}\n\n#Study Materials\n{study_materials}\n\n"
    response = {
        'course_description' : course_description,
        'course_objectives'  : course_objectives,
        'study_materials'    : study_materials,
        'course_outline'     : course_outline,
        'grading_policy'     : grading_policy,
        'rules_policies'     : rules_policies,
        }

    return response
    
