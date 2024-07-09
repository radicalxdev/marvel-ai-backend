import unittest
from io import BytesIO
from app.features.dynamo.tools import TextSubLoader
from app.services.logger import setup_logger

class TestTextSubLoader(unittest.TestCase):
    def setUp(self):
        self.logger = setup_logger(__name__)

        # Create sample text content
        self.sample_text_content = BytesIO(b'Hello, World!')

        # Create empty text content for edge case
        self.empty_text_content = BytesIO(b'')

    def test_load_normal_case(self):
        loader = TextSubLoader(self.sample_text_content, 'txt')
        documents = loader.load()
        self.assertTrue(len(documents) > 0)
        self.assertEqual(documents[0].page_content, 'Hello, World!')

    def test_load_empty_text(self):
        loader = TextSubLoader(self.empty_text_content, 'txt')
        documents = loader.load()
        self.assertEqual(len(documents), 1)
        self.assertEqual(documents[0].page_content.strip(), '')

if __name__ == '__main__':
    unittest.main()
