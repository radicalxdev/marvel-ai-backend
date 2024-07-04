import unittest
from io import BytesIO
from app.features.dynamo.tools import JsonSubLoader
from app.services.logger import setup_logger

class TestJsonSubLoader(unittest.TestCase):
    def setUp(self):
        self.logger = setup_logger(__name__)
        self.sample_json_content = BytesIO(b'{"key": "value"}')

    def test_load(self):
        loader = JsonSubLoader(self.sample_json_content, 'json')
        documents = loader.load()
        self.assertTrue(len(documents) > 0)
        self.assertIn('"key": "value"', documents[0].page_content)

if __name__ == '__main__':
    unittest.main()
