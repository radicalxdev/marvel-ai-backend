import unittest
from io import BytesIO
from docx import Document as DocxDocument
from app.features.dynamo.tools import DocxSubLoader
from app.services.logger import setup_logger

class TestDocxSubLoader(unittest.TestCase):
    def setUp(self):
        self.logger = setup_logger(__name__)

        # Create a sample DOCX content
        self.sample_docx_content = self.create_sample_docx("Hello, World!")

        # Create an empty DOCX content for edge case
        self.empty_docx_content = self.create_sample_docx("")

    def create_sample_docx(self, text):
        docx_content = BytesIO()
        doc = DocxDocument()
        doc.add_paragraph(text)
        doc.save(docx_content)
        docx_content.seek(0)
        return docx_content

    def test_load_normal_case(self):
        loader = DocxSubLoader(self.sample_docx_content, 'docx')
        documents = loader.load()
        self.assertTrue(len(documents) > 0)
        self.assertIn('Hello, World!', documents[0].page_content)

    def test_load_empty_docx(self):
        loader = DocxSubLoader(self.empty_docx_content, 'docx')
        documents = loader.load()
        self.assertEqual(len(documents), 1)
        self.assertEqual(documents[0].page_content.strip(), '')  # Check that the content is empty

    def test_load_invalid_docx(self):
        invalid_docx_content = BytesIO(b"This is not a DOCX content")
        loader = DocxSubLoader(invalid_docx_content, 'docx')
        documents = loader.load()
        self.assertEqual(len(documents), 0)  # Expect no documents to be returned

if __name__ == '__main__':
    unittest.main()

