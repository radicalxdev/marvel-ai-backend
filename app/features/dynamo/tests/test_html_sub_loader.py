import unittest
from io import BytesIO
from app.features.dynamo.tools import HtmlSubLoader
from app.services.logger import setup_logger

class TestHtmlSubLoader(unittest.TestCase):
    def setUp(self):
        self.logger = setup_logger(__name__)
        self.sample_html_content = BytesIO(b'<html><body>Hello, World!</body></html>')
        self.empty_html_content = BytesIO(b'')
        self.invalid_html_content = BytesIO(b'This is not an HTML content')

    def test_load_normal_case(self):
        loader = HtmlSubLoader(self.sample_html_content, 'html')
        documents = loader.load()
        self.assertTrue(len(documents) > 0)
        self.assertIn('Hello, World!', documents[0].page_content)

    def test_load_empty_html(self):
        loader = HtmlSubLoader(self.empty_html_content, 'html')
        with self.assertRaises(ValueError):  # Expect a ValueError for empty HTML content
            loader.load()

    def test_load_invalid_html(self):
        loader = HtmlSubLoader(self.invalid_html_content, 'html')
        with self.assertRaises(ValueError):  # Expect a ValueError for invalid HTML content
            loader.load()

if __name__ == '__main__':
    unittest.main()
