import os
import json
import time
import requests
import pandas as pd
from langchain_core.prompts import PromptTemplate
# from langchain_google_vertexai import VertexAI
import re
# from reportlab.lib.pagesizes import letter
# from reportlab.pdfgen import canvas
# from reportlab.platypus import Table, TableStyle
# from reportlab.lib import colors
from docx import Document
from requests.exceptions import HTTPError
from io import BytesIO
# from bs4 import BeautifulSoup
import requests
# import praw
# import prawcore
from app.services.logger import setup_logger
from langchain_groq import ChatGroq
import requests
import os
from io import BytesIO
from PyPDF2 import PdfReader
from docx import Document
#from app.features.syllabus_generator import credentials

import json
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

logger = setup_logger(__name__)

model_name = 'llama-3.1-70b-versatile'
# Entire syllabus generator pipeline with all functions in this class
class RUBRIC:

    def __init__(self,grade,points, standard, assignment,path=""):
        self.grade = grade
        self.points = points
        self.standard = standard
        self.assignment = assignment
        self.path = path
        self.model = ChatGroq(model=model_name,temperature=0.3,api_key="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")

    def read_text_file(self,filepath):

        with open(f"{self.path}{filepath}", 'r') as file:
            return file.read()

    def build_prompt(self,filepath):
        # build invididual promps for each sub part of syllabus
        template = self.read_text_file(filepath)

        prompt = PromptTemplate.from_template(template)
        return prompt

    def validator(self,response):
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
    
    def extract_text_from_txt(self,file_content):
        return file_content.decode('utf-8')

    def extract_text_from_pdf(self,file_content):
        pdf_reader = PdfReader(BytesIO(file_content))
        text = ''
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text

    def extract_text_from_docx(self,file_content):
        doc = Document(BytesIO(file_content))
        text = '\n'.join([para.text for para in doc.paragraphs])
        return text

    def download_file(self,url):
        response = requests.get(url)
        if response.status_code == 200:
            content_type = response.headers['Content-Type']
            return response.content, content_type
        else:
            raise Exception(f"Failed to download the file. Status code: {response.status_code}")

    def extract_content_from_url(self,file_url):
        file_content, content_type = self.download_file(file_url)

        # Check the Content-Type header for file type
        if 'application/pdf' in content_type:
            print("Extracting content from PDF...")
            return self.extract_text_from_pdf(file_content)
        elif 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' in content_type:
            print("Extracting content from Word Document (.docx)...")
            return self.extract_text_from_docx(file_content)
        elif 'text/plain' in content_type or 'text/html' in content_type:
            print("Extracting content from Text File...")
            return self.extract_text_from_txt(file_content)
        else:
            raise Exception(f"Unsupported file type: {content_type}. Unable to extract content.")
    
    def genpdf(self,rubric_data):
                # Create a PDF document
        # Create a PDF document
        pdf_file = "dynamic_rubric.pdf"
        pdf = SimpleDocTemplate(pdf_file, pagesize=letter)

        # Prepare styles
        styles = getSampleStyleSheet()

        # Table header (dynamic for each category)
        #table_data = [['Criteria', 'Exceptional (4.0)', 'Good (3.0-3.9)', 'Fair (2.0-2.9)', 'Needs Improvement (0.0-1.9)']]
        
        table_data = [] #
        table_data.append(['Criteria'] + [str(i.keys()) for i in rubric_data])
        print(table_data)
        # Parse rubric data into table rows dynamically
        for item in rubric_data:
            for criteria, category in item.items():
                # Add criteria header row dynamically
                # Add rating descriptions dynamically for each category
                categories = list(category)
                print(categories)
                table_data.append([
                    Paragraph(f"<b>{criteria}</b>", styles['Normal']),
                    Paragraph(category.get(categories[0], ''), styles['Normal']),
                    Paragraph(category.get(categories[1], ''), styles['Normal']),
                    Paragraph(category.get(categories[2], ''), styles['Normal']),
                    Paragraph(category.get(categories[3], ''), styles['Normal'])
                ])

        # Create a table with dynamic content and column widths
        table = Table(table_data, colWidths=[150, 100, 100, 100, 100])

        # Add styles for the table (adjust for layout matching your PDF)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),  # Header row background color
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),  # Header row text color
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),  # Left-align text
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Bold font for the header
            ('FONTSIZE', (0, 0), (-1, -1), 10),  # Font size for the whole table
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),  # Padding for the header row
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),  # Background color for body rows
            ('GRID', (0, 0), (-1, -1), 1, colors.black)  # Add grid lines
        ]))

        # Build the PDF
        elements = [table]
        pdf.build(elements)

       

        print(f"PDF created successfully at {pdf_file}")

    def run(self):
        # Important study resources and their specific function

        prompt = self.build_prompt('/Users/vedanthaggarwal/Documents/RADICAL1/marvel-ai-backend/app/features/rubric_generator/prompts/prompt.txt')
        chain = prompt | self.model
        assignment_content = self.extract_content_from_url(self.assignment)
        print(assignment_content)
        response = chain.invoke(
                        {
                            'grade' : self.grade,
                            'points':self.points,
                            'assignment' : assignment_content,
                            'standard':self.standard
                        })
        print(response.content)
        response = self.validator(response.content)
        self.genpdf(response)
        print(response)
        return response