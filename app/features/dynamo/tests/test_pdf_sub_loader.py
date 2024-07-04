import unittest
from io import BytesIO
from app.features.dynamo.tools import PDFSubLoader
from app.services.logger import setup_logger
from fpdf import FPDF
import tempfile

class TestPDFSubLoader(unittest.TestCase):
    def setUp(self):
        self.logger = setup_logger(__name__)
        self.sample_pdf_content = BytesIO()

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Hello, World!", ln=True, align="C")
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            pdf.output(tmp_file.name)
            tmp_file.seek(0)
            self.sample_pdf_content = BytesIO(tmp_file.read())

    def test_load(self):
        loader = PDFSubLoader(self.sample_pdf_content, 'pdf')
        documents = loader.load()
        self.assertTrue(len(documents) > 0)
        self.assertIn('Hello, World!', documents[0].page_content)

if __name__ == '__main__':
    unittest.main()

