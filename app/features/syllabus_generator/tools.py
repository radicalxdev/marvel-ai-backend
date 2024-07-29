# from bs4 import BeautifulSoup
import requests
import os
import re
import json
from dotenv import load_dotenv
from pathlib import Path
import time

from langchain_core.prompts import PromptTemplate
from langchain_google_vertexai import VertexAI
import json
import pandas as pd

from app.services.logger import setup_logger
# from app.services.tool_registry import ToolFile
# from app.api.error_utilities import LoaderError
env_path = Path(__file__).resolve().parents[2] / '.env'
load_dotenv(dotenv_path=env_path)

relative_path = "app/features/syllabus_generator/"

logger = setup_logger(__name__)

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "local-auth.json"


class Search_engine :
    
    def __init__(self,grade,subject,API_KEY,SEARCH_ENGINE_ID):
        self.grade = grade
        self.subject = subject
        self.API_KEY = API_KEY
        self.SEARCH_ENGINE_ID = SEARCH_ENGINE_ID
        
    def scrap_data(self):
        url = 'https://www.googleapis.com/customsearch/v1'

        params = {
            'q': f'syllabus of {self.subject} {self.grade} level',
            'key': self.API_KEY,
            'cx': self.SEARCH_ENGINE_ID
        }

        response = requests.get(url,params=params).json()
        links = [item['link'] for item in response['items']]
        return links[0]

    def get_web_results(self):
        # we scrap the link to find the tables components and store them in listes
        link = self.scrap_data()
        return pd.read_html(link)
 

class Syllabus_generator :
    
    def __init__(self,grade,subject,Syllabus_type,API_KEY,SEARCH_ENGINE_ID,path=""):
        self.grade = grade
        self.subject = subject
        self.Syllabus_type = Syllabus_type
        self.model = VertexAI(model_name='gemini-pro',temperature=0.1)
        self.path = path
        Engine = Search_engine(grade,subject,API_KEY,SEARCH_ENGINE_ID)
        self.web_search = Engine.get_web_results()
        
    def read_text_file(self,filepath):
        
        with open(f"{self.path}/{filepath}", 'r') as file:
            return file.read()
        
    def build_prompt(self,filepath):

        template = self.read_text_file(filepath)

        prompt = PromptTemplate.from_template(template)
        return prompt

    def Validator(self,response):
        # prompt = self.build_prompt('prompts/Output_validation.txt')
        # chain = prompt | self.model
        # response = chain.invoke({"input":input})
        data = ""
        try:
            data = json.loads(response)
        except json.JSONDecodeError as e:
            print("JSON Decode Error , Trying to correct the JSON")
            try:
                corrected_result = response[response.find('['):response.rfind(']') + 1]
                data = json.loads(corrected_result)
                print("Corrected Parsed JSON successfully")
            except json.JSONDecodeError as e:
                print("Failed to parse corrected JSON")
        return data
        
    def course_description(self) -> str:
        
        prompt = self.build_prompt('prompts/course_description.txt')
        chain = prompt | self.model
        
        response = chain.invoke({"grade":self.grade,"subject":self.subject,"Syllabus_type":self.Syllabus_type})
        return response

    def course_objectives(self,course_description:str) -> str:

        prompt = self.build_prompt('prompts/course_objectives.txt')
        chain = prompt | self.model
        
        response = chain.invoke(
                        {
                            'grade' : self.grade, 
                            'subject' : self.subject, 
                            'Syllabus_type' : self.Syllabus_type, 
                            'course_description': course_description
                        })
        
        return self.Validator(response)
        
    def course_outline(self,course_description:str,course_objectives:str) -> str:
        Outline_prompt = self.build_prompt('prompts/course_outline.txt')
        Search_prompt = self.build_prompt('prompts/search_results.txt')

        chain1 = Search_prompt | self.model
        search_results = chain1.invoke(
                               {
                                   'grade' : self.grade,
                                    'subject' : self.subject,
                                    'Syllabus_type' : self.Syllabus_type,
                                    'web_search' : self.web_search
                               })

        chain2 = Outline_prompt | self.model
        response = chain2.invoke(
                         {
                             'grade' : self.grade,
                             'subject' : self.subject,
                             'Syllabus_type' : self.Syllabus_type,
                             'search_results' : search_results,
                             'course_objectives' : course_objectives,
                             'course_description' : course_description,
                         })
        
        return self.Validator(response)

    def grading_policy(self,course_outline:str) -> str:
        
        prompt = self.build_prompt('prompts/grading_policy.txt')
        chain = prompt | self.model
        
        response = chain.invoke(
                        {
                            'grade' : self.grade,
                            'subject' : self.subject,
                            'Syllabus_type' : self.Syllabus_type,
                            'course_outline' : course_outline
                        })

        return response

    def rules_policies(self,course_outline:str) -> str:
        
        prompt = self.build_prompt('prompts/rules_policies.txt')
        chain = prompt | self.model
        
        response = chain.invoke(
                        {
                            'grade' : self.grade,
                            'subject' : self.subject,
                            'Syllabus_type' : self.Syllabus_type,
                            'course_outline' : course_outline
                        })
        
        return self.Validator(response)

    def study_materials(self,course_outline:str) -> str:
        prompt = self.build_prompt('prompts/study_materials.txt')
        chain = prompt | self.model
        
        response = chain.invoke(
                        {
                            'grade' : self.grade,
                            'subject' : self.subject,
                            'Syllabus_type' : self.Syllabus_type,
                            'course_outline' : course_outline
                        })
        return self.Validator(response)

    def run(self,verbose=False):
        
        #? I added these time.sleep to avoid the quota increase error because if you use a free trial these a limit of requests per minute
        
        course_description = self.course_description()
        time.sleep(10)
        course_objectives = self.course_objectives(course_description)
        time.sleep(10)
        course_outline = self.course_outline(course_description,course_objectives)
        time.sleep(10)
        grading_policy = self.grading_policy(course_outline)
        time.sleep(10)
        rules_policies = self.rules_policies(course_outline)
        time.sleep(10)
        study_materials = self.study_materials(course_outline)
        
        response = {
            'course_description':course_description,
            'course_objectives' :course_objectives,
            'study_materials'   :study_materials,
            'course_outline'    :course_outline,
            'grading_policy'    :grading_policy,
            'rules_policies'    :rules_policies
        }
        
        if verbose :
            for section_name,section_content in response:
                print("\n"+"*"*100)
                print(f"The results of {section_name} are :\n {section_content}")
                
        return response
