import os
import json
import time
import requests
import pandas as pd
from langchain_core.prompts import PromptTemplate
from langchain_google_vertexai import VertexAI
import re
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
from docx import Document
from requests.exceptions import HTTPError
from io import BytesIO
from bs4 import BeautifulSoup
import requests
import praw
import prawcore
from app.services.logger import setup_logger
from langchain_groq import ChatGroq
#from app.features.syllabus_generator import credentials

logger = setup_logger(__name__)

model_name = 'llama-3.1-70b-versatile'
# Entire syllabus generator pipeline with all functions in this class
class AI_resistant :

    def __init__(self,grade,assignment,path=""):
        self.grade = grade
        self.assignment = assignment
        self.model = ChatGroq(model=model_name,temperature=0.3,api_key="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")

    def read_text_file(self,filepath):

        with open(f"{self.path}{filepath}", 'r') as file:
            return file.read()

    def build_prompt(self,filepath):
        # build invididual promps for each sub part of syllabus
        template = self.read_text_file(filepath)

        prompt = PromptTemplate.from_template(template)
        return prompt

    def Validator(self,response):
        data = []
        try:
            data = json.loads(response)
        except json.JSONDecodeError as e:

           
            print("JSON Decode Error , Trying to correct the JSON")
            try:
                corrected_result = response[min(response.find('{'),response.find('[')):max(response.rfind(']'),response.rfind('}')) + 1]
                data = json.loads(corrected_result)
                print("Corrected Parsed JSON successfully")
            except json.JSONDecodeError as e:
                print("Failed to parse corrected JSON")
        return data

    def run(self):
        # Important study resources and their specific function

        prompt = self.build_prompt('prompts/prompt.txt')
        chain = prompt | self.model

        response = chain.invoke(
                        {
                            'grade' : self.grade,
                            'assignment' : self.assignment,
                        })
        response = self.Validator(response)
        print(response)
        return response
    
# Search engine class to extract api output and verify data
'''
class Search_engine:

    def __init__(self, grade, subject, API_KEY=credentials['api_key'],SEARCH_ENGINE_ID=credentials['search_engine_id']):
        self.grade = grade
        self.subject = subject
        self.API_KEY = API_KEY
        self.SEARCH_ENGINE_ID = SEARCH_ENGINE_ID

    def get_link(self):
        url = 'https://www.googleapis.com/customsearch/v1'
        params = {
            'q': f'syllabus of {self.subject} {self.grade} level',
            'key': self.API_KEY,
            'cx': self.SEARCH_ENGINE_ID
        }
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        try:
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()
            links = [item['link'] for item in data.get('items', [])]
            if not links:
                print("No links found in the search results.")
            return links[0]
        except HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")  # Log the error
            return ''
        except Exception as err:
            print(f"Other error occurred: {err}")  # Log the error
            return ''
        return ''

    def scrap_data(self):
        link = self.get_link()
        if not link :
            return []
        try:
            return pd.read_html(link)
        except ValueError as e:
            print(f"Error scraping data: {e}")  # Handle and log the scraping error
            return []
'''
