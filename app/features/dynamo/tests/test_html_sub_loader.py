import unittest
from io import BytesIO
from app.features.dynamo.tools import HtmlSubLoader
from app.services.logger import setup_logger

class TestHtmlSubLoader(unittest.TestCase):
    def setUp(self):
        self.logger = setup_logger(__name__)
        self.sample_html_content = BytesIO(b'<html><body>Hello, World!</body></html>')

    def test_load(self):
        loader = HtmlSubLoader(self.sample_html_content, 'html')
        documents = loader.load()
        self.assertTrue(len(documents) > 0)
        self.assertIn('Hello, World!', documents[0].page_content)

if __name__ == '__main__':
    unittest.main()
