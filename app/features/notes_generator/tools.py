import os
import re
from typing import Optional
import pytesseract
from pdfminer.high_level import extract_text as extract_pdf
import docx
import csv
import requests
from bs4 import BeautifulSoup
from youtube_transcript_api import YouTubeTranscriptApi
from docx import Document
from fpdf import FPDF

from io import StringIO

from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser

def extract_text_from_file(file_path: str) -> str:
    """extract text based on file type."""
    if file_path.endswith('.pdf'): #Note this part 
        return extract_pdf(file_path)
    elif file_path.endswith('.docx'):
        doc = docx.Document(file_path)
        return '\n'.join([p.text for p in doc.paragrphas])
    elif file_path.endswith('.csv'):
        with open(file_path, 'r') as f:
            reader = csv.reader(f)
            return '\n'.join([' '.join(row) for row in reader])
    elif file_path.endswith('txt'):
        with open(file_path, 'r') as f:
            return f.read()
    else:
        raise ValueError("Unsupprted file type.")



def extract_text_from_url(video_url: str) -> str:
    """Extract text from a website URL"""
    video_id = video_url.split("v=")[-1]
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
    return ' '.join([item['text'] for item in transcript])

def generate_notes(content: str, focus_topic: Optional[str], structure: str) -> str:
    """Generate notes using a summarization tool or AI-driven prompt."""
    # Too be replace with AI tool integration (OpenAI API, Hugging Face)
    notes = f"Focus: {focus_topic}\n\nContent:\n{content}"
    return notes  # Placeholder logic



def export_notes(notes: str, format_type: str) -> str:
    """Export notes to the specified file format."""
    # Get the absolute path to the `outputs` directory
    base_dir = os.path.dirname(os.path.abspath(__file__))  # Get the directory where the script is located
    output_dir = os.path.join(base_dir, "outputs")
    
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Construct the file path
    file_path = os.path.join(output_dir, f"notes_output.{format_type}")
    file_path = f"outputs/notes_output.{format_type}"
    if format_type == 'txt':
        with open(file_path, 'w') as f:
            f.write(notes)
    elif format_type == 'docx':
        doc = Document()
        doc.add_paragraph(notes)
        doc.save(file_path)
    elif format_type == 'pdf':
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        for line in notes.split("\n"):
            pdf.cell(200, 10, txt=line, ln=True)
        pdf.output(file_path)
    return file_path

