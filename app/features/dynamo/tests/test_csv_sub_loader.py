import unittest
from io import BytesIO
from app.features.dynamo.tools import CsvSubLoader
from app.services.logger import setup_logger

class TestCsvSubLoader(unittest.TestCase):
    def setUp(self):
        self.logger = setup_logger(__name__)
        self.sample_csv_content = BytesIO(b'header1,header2\nvalue1,value2')
        self.empty_csv_content = BytesIO(b'')
        self.invalid_csv_content = BytesIO(b'This is not a CSV content')

    def test_load_normal_case(self):
        loader = CsvSubLoader(self.sample_csv_content, 'csv')
        documents = loader.load()
        self.assertTrue(len(documents) > 0)
        self.assertIn('header1,header2', documents[0].page_content)
        self.assertIn('value1,value2', documents[0].page_content)

    def test_load_empty_csv(self):
        loader = CsvSubLoader(self.empty_csv_content, 'csv')
        with self.assertRaises(ValueError):  # Expect a ValueError for empty CSV content
            loader.load()

    def test_load_invalid_csv(self):
        loader = CsvSubLoader(self.invalid_csv_content, 'csv')
        with self.assertRaises(ValueError):  # Expect a ValueError for invalid CSV content
            loader.load()

if __name__ == '__main__':
    unittest.main()
