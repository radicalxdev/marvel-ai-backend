import os
import requests
from typing import Union
from urllib.parse import urlparse


def export_output(text: str, export_format: str) -> str:
    """
    Export the rewritten text to the specified format.

    Args:
        text (str): The rewritten text content.
        export_format (str): Output format ('txt', 'docx', 'pdf').

    Returns:
        str: Path to the exported file.
    """
    output_dir = "outputs"
    os.makedirs(output_dir, exist_ok=True)

    if export_format == "txt":
        output_path = os.path.join(output_dir, "output.txt")
        with open(output_path, "w") as file:
            file.write(text)
    elif export_format == "docx":
        from docx import Document
        doc = Document()
        doc.add_paragraph(text)
        output_path = os.path.join(output_dir, "output.docx")
        doc.save(output_path)
    elif export_format == "pdf":
        from fpdf import FPDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, text)
        output_path = os.path.join(output_dir, "output.pdf")
        pdf.output(output_path)
    else:
        raise ValueError("Unsupported export format.")

    return output_path


def process_url_input(url: str) -> str:
    """
    Fetch text content from a URL.

    Args:
        url (str): The URL to fetch data from.

    Returns:
        str: Extracted text content.
    """
    # Validate URL format
    parsed_url = urlparse(url)
    if not (parsed_url.scheme and parsed_url.netloc):
        raise ValueError("Invalid URL format.")

    try:
        response = requests.get(url, timeout=10)  # Add timeout for safety
        response.raise_for_status()  # Raise exception for HTTP errors
        return response.text
    except requests.exceptions.RequestException as e:
        raise ValueError(f"Failed to fetch URL content. Error: {str(e)}")