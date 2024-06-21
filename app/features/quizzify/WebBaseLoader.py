from typing import List, Sequence
from langchain_core.documents import Document
from bs4 import BeautifulSoup
import requests
from langchain_community.document_loaders import WebBaseLoader

class CustomWebPageLoader:
    def __init__(self, web_paths: Sequence[str], verbose=False, **kwargs):
        self.loader = WebBaseLoader(web_paths=web_paths, **kwargs)
        self.verbose = verbose

    def load(self) -> List[Document]:
        documents = []

        for url in self.loader.web_paths:
            try:
                response = requests.get(url)
                response.raise_for_status()  # Raise an error for bad status codes

                # Specify the encoding when parsing HTML content
                soup = BeautifulSoup(response.content, 'lxml', from_encoding=response.encoding)
                

                # Find all heading tags (h1, h2, h3)
                headings = [heading.get_text().strip() for heading in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'h3 + span'])]

                # Find all paragraph tags
                paragraphs = [paragraph.get_text().strip() for paragraph in soup.find_all('p')]

                # Combine headings and paragraphs
                combined_content = "\n".join(headings + paragraphs)

                if combined_content:
                    # Create a Document instance with combined content and metadata
                    metadata = {"source": url}
                    new_doc = Document(page_content=combined_content, metadata=metadata)
                    documents.append(new_doc)

                if self.verbose:
                    if documents:
                        print(f"Successfully loaded content from {url}")
                    else:
                        print(f"No relevant content found at {url}")
            except Exception as e:
                if self.verbose:
                    print(f"Failed to load content from {url}")
                    print(e)

        if not documents and self.verbose:
            print("Unable to load any content from the URLs")

        return documents


# Example usage
if __name__ == "__main__":
    url = "https://en.wikipedia.org/wiki/United_States"  # Replace with your desired URL
    loader = CustomWebPageLoader(web_paths=[url], verbose=True)
    documents = loader.load()
    for doc in documents:
        print(doc.page_content)