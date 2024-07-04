import unittest
from io import BytesIO
from app.features.dynamo.tools import TextSubLoader
from app.services.logger import setup_logger

class TestTextSubLoader(unittest.TestCase):
    def setUp(self):
        self.logger = setup_logger(__name__)
        self.sample_text_content = BytesIO(b'Hello, World!')

    def test_load(self):
        loader = TextSubLoader(self.sample_text_content, 'txt')
        documents = loader.load()
        self.assertTrue(len(documents) > 0)
        self.assertEqual(documents[0].page_content, 'Hello, World!')

if __name__ == '__main__':
    unittest.main()
