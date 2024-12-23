import unittest
import pandas as pd
import os
from unittest.mock import patch
from app.tools.notes_generator.document_loaders import load_csv_documents, load_xls_documents, load_xlsx_documents, load_xml_documents, FileHandlerError
import io


# Create a dummy data folder if it doesn't exist
TEST_DATA_FOLDER = "test_data"
if not os.path.exists(TEST_DATA_FOLDER):
    os.makedirs(TEST_DATA_FOLDER)

# Create dummy CSV
def create_dummy_csv():
    csv_data = {
        'Name': ['Alice', 'Bob', 'Charlie'],
        'Age': [25, 30, 28],
        'City': ['New York', 'London', 'Paris']
    }
    df = pd.DataFrame(csv_data)
    csv_file_path = os.path.join(TEST_DATA_FOLDER, "dummy.csv")
    df.to_csv(csv_file_path, index=False)
    return csv_file_path

# Create dummy XLSX
def create_dummy_xls():
    xls_data = {
        'Category': ['A', 'B', 'C'],
        'Value': [10, 20, 30]
    }
    df = pd.DataFrame(xls_data)
    xls_file_path = os.path.join(TEST_DATA_FOLDER, "dummy.xlsx")
    df.to_excel(xls_file_path, index=False)
    return xls_file_path

# Create dummy XLSX
def create_dummy_xlsx():
    xlsx_data = {'Item': ['X', 'Y', 'Z'], 'Count': [100, 200, 300]}
    df = pd.DataFrame(xlsx_data)
    xlsx_file_path = os.path.join(TEST_DATA_FOLDER, "dummy.xlsx")
    df.to_excel(xlsx_file_path, index=False, engine="openpyxl")  # Ensure openpyxl is used
    print(f"Created dummy XLSX file: {xlsx_file_path}")  # Debugging info
    return xlsx_file_path


# Create dummy XML
def create_dummy_xml():
    xml_data = """
    <data>
        <record>
            <field1>val1</field1>
            <field2>val2</field2>
        </record>
        <record>
            <field1>val3</field1>
            <field2>val4</field2>
        </record>
    </data>
    """
    xml_file_path = os.path.join(TEST_DATA_FOLDER, "dummy.xml")
    with open(xml_file_path, 'w') as f:
        f.write(xml_data)
    return xml_file_path


class TestDocumentLoading(unittest.TestCase):
    def setUp(self):
       # Create dummy files
        self.csv_file_path = create_dummy_csv()
        self.xls_file_path = create_dummy_xls()
        self.xlsx_file_path = create_dummy_xlsx()
        self.xml_file_path = create_dummy_xml()

    def tearDown(self):
         # Delete dummy files
        os.remove(self.csv_file_path)
        os.remove(self.xls_file_path)
        os.remove(self.xml_file_path)
    
    @patch('app.features.notes_generator.document_loaders.model')
    def test_load_csv_documents(self,mock_model):
        mock_model.return_value="This is a test."
        docs = load_csv_documents(self.csv_file_path)
        self.assertIsNotNone(docs)
        self.assertTrue(isinstance(docs, list))
        self.assertTrue(len(docs) > 0)
        self.assertTrue(len(docs[0].page_content) > 0) # Check that there is some content
    
    @patch('app.features.notes_generator.document_loaders.model')
    def test_load_xls_documents(self,mock_model):
        mock_model.return_value="This is a test."
        docs = load_xls_documents(self.xls_file_path)
        self.assertIsNotNone(docs)
        self.assertTrue(isinstance(docs, list))
        self.assertTrue(len(docs) > 0)
        self.assertTrue(len(docs[0].page_content) > 0) # Check that there is some content
    
    @patch('app.features.notes_generator.document_loaders.model')
    def test_load_xlsx_documents(self,mock_model):
        mock_model.return_value="This is a test."
        docs = load_xlsx_documents(self.xlsx_file_path)
        self.assertIsNotNone(docs)
        self.assertTrue(isinstance(docs, list))
        self.assertTrue(len(docs) > 0)
        self.assertTrue(len(docs[0].page_content) > 0) # Check that there is some content
    
    @patch('app.features.notes_generator.document_loaders.model')
    def test_load_xml_documents(self,mock_model):
        mock_model.return_value="This is a test."
        docs = load_xml_documents(self.xml_file_path)
        self.assertIsNotNone(docs)
        self.assertTrue(isinstance(docs, list))
        self.assertTrue(len(docs) > 0)
        self.assertTrue(len(docs[0].page_content) > 0) # Check that there is some content

    def test_load_csv_documents_invalid(self):
        with self.assertRaises(FileNotFoundError):
            load_csv_documents("invalid_path.csv")

    def test_load_xls_documents_invalid(self):
        with self.assertRaises(FileNotFoundError):
             load_xls_documents("invalid_path.xls")

    def test_load_xlsx_documents_invalid(self):
        with self.assertRaises(FileNotFoundError):
             load_xlsx_documents("invalid_path.xlsx")

    def test_load_xml_documents_invalid(self):
         with self.assertRaises(FileNotFoundError):
            load_xml_documents("invalid_path.xml")

if __name__ == '__main__':
    unittest.main()