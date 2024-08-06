import unittest
from io import BytesIO
from app.features.dynamo.tools import MarkdownSubLoader
from app.services.logger import setup_logger

class TestMarkdownSubLoader(unittest.TestCase):
    def setUp(self):
        self.logger = setup_logger(__name__)

        # Create a sample Markdown content
        self.sample_md_content = BytesIO(b'# Hello, World!')

        # Create an empty Markdown content for edge case
        self.empty_md_content = BytesIO(b'')

        # Create invalid Markdown content
        self.invalid_md_content = BytesIO(b'test')

    def test_load_normal_case(self):
        loader = MarkdownSubLoader(self.sample_md_content, 'md')
        documents = loader.load()
        self.assertTrue(len(documents) > 0)
        self.assertIn('# Hello, World!', documents[0].page_content)

    def test_load_empty_md(self):
        loader = MarkdownSubLoader(self.empty_md_content, 'md')
        documents = loader.load()
        self.assertEqual(len(documents), 1)
        self.assertEqual(documents[0].page_content.strip(), '')

    def test_load_invalid_md(self):
        loader = MarkdownSubLoader(self.invalid_md_content, 'md')
        documents = loader.load()
        self.assertEqual(len(documents), 1)
        self.assertEqual(documents[0].page_content.strip(), '')

if __name__ == '__main__':
    unittest.main()

