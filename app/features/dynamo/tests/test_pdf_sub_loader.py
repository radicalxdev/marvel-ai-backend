import unittest
from io import BytesIO
from app.features.dynamo.tools import PDFSubLoader
from app.services.logger import setup_logger
from fpdf import FPDF
import tempfile

class TestPDFSubLoader(unittest.TestCase):
    def setUp(self):
        self.logger = setup_logger(__name__)

        # Create a sample PDF content
        self.sample_pdf_content = self.create_sample_pdf("Hello, World!")

        # Create an empty PDF content for edge case
        self.empty_pdf_content = self.create_sample_pdf("")

    def create_sample_pdf(self, text):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt=text, ln=True, align="C")
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            pdf.output(tmp_file.name)
            tmp_file.seek(0)
            return BytesIO(tmp_file.read())

    def test_load_normal_case(self):
        loader = PDFSubLoader(self.sample_pdf_content, 'pdf')
        documents = loader.load()
        self.assertTrue(len(documents) > 0)
        self.assertIn('Hello, World!', documents[0].page_content)

    def test_load_empty_pdf(self):
        loader = PDFSubLoader(self.empty_pdf_content, 'pdf')
        documents = loader.load()
        self.assertEqual(len(documents), 1)
        self.assertEqual(documents[0].page_content.strip(), '')

    def test_load_invalid_pdf(self):
        invalid_pdf_content = BytesIO(b"This is not a PDF content")
        loader = PDFSubLoader(invalid_pdf_content, 'pdf')
        documents = loader.load()
        self.assertEqual(len(documents), 0) 

if __name__ == '__main__':
    unittest.main()
