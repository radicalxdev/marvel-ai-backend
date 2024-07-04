import unittest
from io import BytesIO
from docx import Document as DocxDocument
from app.features.dynamo.tools import DocxSubLoader
from app.services.logger import setup_logger

class TestDocxSubLoader(unittest.TestCase):
    def setUp(self):
        self.logger = setup_logger(__name__)
        self.sample_docx_content = BytesIO()
        doc = DocxDocument()
        doc.add_paragraph("Hello, World!")
        doc.save(self.sample_docx_content)
        self.sample_docx_content.seek(0)

    def test_load(self):
        loader = DocxSubLoader(self.sample_docx_content, 'docx')
        documents = loader.load()
        self.assertTrue(len(documents) > 0)
        self.assertIn('Hello, World!', documents[0].page_content)

if __name__ == '__main__':
    unittest.main()
