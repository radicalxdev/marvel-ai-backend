from docx import Document
from pdfminer.high_level import extract_text as extract_pdf_text

def parse_pdf(file_path):
    """Extract text from a PDF file."""
    return extract_pdf_text(file_path)

def parse_docx(file_path):
    """Extract text from a DOCX file."""
    doc = Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs])