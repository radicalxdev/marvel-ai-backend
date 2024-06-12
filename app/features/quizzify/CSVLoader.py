from typing import List
import pandas as pd
from langchain_core.documents import Document

class CSVLoader:
    def __init__(self):
        """
        Initializes the CSVLoader.
        """
        pass

    def load(self, file_paths: List[str]) -> List[Document]:
        """
        Loads CSV files and converts them into Document objects.

        :param file_paths: List of file paths representing the files to load.
        :return: List of Document objects.
        """
        documents = []
        for file_path in file_paths:
            file_type = file_path.split(".")[-1]

            if file_type.lower() != "csv":
                raise ValueError(f"Unsupported file type: {file_type}")

            df = pd.read_csv(file_path)
            csv_content = df.to_string()

            metadata = {"source": "CSV", "file_name": file_path}
            doc = Document(page_content=csv_content, metadata=metadata)
            documents.append(doc)

        return documents

# Example usage
if __name__ == "__main__":
    file_paths = ["C:/Users/Fahira/Downloads/customers-100.csv"] 
    loader = CSVLoader()
    documents = loader.load(file_paths)
    for doc in documents:
        print(doc.page_content)
