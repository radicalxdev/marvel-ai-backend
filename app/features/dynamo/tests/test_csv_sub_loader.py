import unittest
from io import BytesIO
from app.features.dynamo.tools import CsvSubLoader
from app.services.logger import setup_logger

class TestCsvSubLoader(unittest.TestCase):
    def setUp(self):
        self.logger = setup_logger(__name__)
        self.sample_csv_content = BytesIO(b'header1,header2\nvalue1,value2')

    def test_load(self):
        loader = CsvSubLoader(self.sample_csv_content, 'csv')
        documents = loader.load()
        self.assertTrue(len(documents) > 0)
        self.assertIn('header1, header2', documents[0].page_content)
        self.assertIn('value1, value2', documents[0].page_content)

if __name__ == '__main__':
    unittest.main()

