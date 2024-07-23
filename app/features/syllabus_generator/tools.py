# This is code for quizzify repurpose for syllabus generator
### MINI FUNCTIONS FOR EAC SUB PART OF THE SYLLABUS AND THEN ONE FINAL FUNCTION TO COMBINE THE OUTPUT

from typing import List, Tuple, Dict, Any
from io import BytesIO
from fastapi import UploadFile
from pypdf import PdfReader
from urllib.parse import urlparse
from bs4 import BeautifulSoup
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

relative_path = "features/syllabus_generator"

logger = setup_logger(__name__)

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r'abolute file path'


# All functions and procedures program requires should be in tools.py
def scrap_data(grade,subject,API_KEY,SEARCH_ENGINE_ID):
    # We use the google api to get the results of the search 'syllabus of {subject} {grade} level' then we extract the first link
    
    url = 'https://www.googleapis.com/customsearch/v1'

    params = {
        'q': f'syllabus of {subject} {grade} level',
        'key': API_KEY,
        'cx': SEARCH_ENGINE_ID
    }

    response = requests.get(url,params=params).json()
    links = [item['link'] for item in response['items']]
    return links[0]

def get_table_from_link(link):
    # we scrap the link to find the tables components and store them in listes
    
    response = requests.get(link)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find all tables
    tables = soup.find_all('table')
    # Extract table content
    table_data = []
    for table in tables:
        rows = table.find_all('tr')
        table_content = []
        for row in rows:
            cells = row.find_all(['td', 'th'])
            cell_text = [cell.get_text(strip=True) for cell in cells]
            table_content.append(cell_text)
        table_data.append(table_content)
    
    return str(table_data)
    
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

def course_outline(grade:str,subject:str,course_description:str,course_objectives:str,search_results:str,custom_info='None') -> str:
    link = scrap_data(grade,subject)
    scraped_data = get_table_from_link(link)
    Outline_prompt = build_prompt('prompts/course_outline.txt')
    Search_prompt = build_prompt('prompts/search_results.txt')
    model = GoogleGenerativeAI(model="gemini-1.0-pro")
    
    chain1 = Search_prompt | model
    search_results = chain1.invoke({"scraped_data":scraped_data})
    
    chain2 = Outline_prompt | model
    response = chain2.invoke({'grade':grade,
                              'subject':subject,
                              'custom_info':custom_info,
                              'search_results':search_results,
                              'course_objectives':course_objectives,
                              'course_description':course_description,
                              })
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
    #prompt = read_text_file('prompt/course_description.txt')
    #prompt = PromptTemplate.format(prompt)
    response = {
        'course_description':course_description,
        'course_objectives' :course_objectives,
        'study_materials'   :study_materials,
        'course_outline'    :course_outline,
        'grading_policy'    :grading_policy,
        'rules_policies'    :rules_policies
    }

    return response
    
