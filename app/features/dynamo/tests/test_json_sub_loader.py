import unittest
from io import BytesIO
from app.features.dynamo.tools import JsonSubLoader
from app.services.logger import setup_logger

class TestJsonSubLoader(unittest.TestCase):
    def setUp(self):
        self.logger = setup_logger(__name__)
        self.sample_json_content = BytesIO(b'{"key": "value"}')
        self.empty_json_content = BytesIO(b'{}')
        self.invalid_json_content = BytesIO(b'This is not a JSON content')

    def test_load_normal_case(self):
        loader = JsonSubLoader(self.sample_json_content, 'json')
        documents = loader.load()
        self.assertTrue(len(documents) > 0)
        self.assertIn('"key": "value"', documents[0].page_content)

    def test_load_empty_json(self):
        loader = JsonSubLoader(self.empty_json_content, 'json')
        documents = loader.load()
        self.assertEqual(len(documents), 1)
        self.assertEqual(documents[0].page_content.strip(), '{}')  # Check that the content is empty JSON

    def test_load_invalid_json(self):
        loader = JsonSubLoader(self.invalid_json_content, 'json')
        with self.assertRaises(ValueError):  # Expect a ValueError for invalid JSON content
            loader.load()

if __name__ == '__main__':
    unittest.main()
