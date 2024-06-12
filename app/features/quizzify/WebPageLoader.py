from typing import List
from langchain_core.documents import Document
from langchain.document_loaders import UnstructuredURLLoader

class WebPageLoader:
    def __init__(self, url: str, verbose=False):
        self.url = url
        self.verbose = verbose

    def load(self) -> List[Document]:
        documents = []

        try:
            loader = UnstructuredURLLoader(urls=[self.url])
            loaded_docs = loader.load()
            for doc in loaded_docs:
                # Extract content and metadata
                page_content = doc.page_content
                metadata = {"source": self.url}
                paragraphs = page_content.split('\n')  # Split content into paragraphs
                combined_content = "\n".join([paragraph.strip() for paragraph in paragraphs if paragraph.strip()])

                # Create a Document instance with page content and metadata
                new_doc = Document(page_content=combined_content, metadata=metadata)
                documents.append(new_doc) 
            
            if self.verbose:
                print(f"Successfully loaded content from {self.url}")
        except Exception as e:
            print(f"Failed to load content from {self.url}")
            print(e)

        if not documents:
            print("Unable to load any content from the URL")

        return documents

# Example usage
if __name__ == "__main__":
    url = "https://see.stanford.edu/materials/aimlcs229/transcripts/MachineLearning-Lecture01.pdf"  # Replace with your desired URL
    loader = WebPageLoader(url=url, verbose=True)
    documents = loader.load()
    for doc in documents:
        print(doc.page_content)