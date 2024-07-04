import unittest
from io import BytesIO
from app.features.dynamo.tools import MarkdownSubLoader
from app.services.logger import setup_logger

class TestMarkdownSubLoader(unittest.TestCase):
    def setUp(self):
        self.logger = setup_logger(__name__)
        self.sample_md_content = BytesIO(b'# Hello, World!')

    def test_load(self):
        loader = MarkdownSubLoader(self.sample_md_content, 'md')
        documents = loader.load()
        self.assertTrue(len(documents) > 0)
        self.assertIn('# Hello, World!', documents[0].page_content)

if __name__ == '__main__':
    unittest.main()
