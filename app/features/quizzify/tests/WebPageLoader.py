from typing import List
from langchain_core.documents import Document
from langchain_community.document_transformers import BeautifulSoupTransformer
import requests

# URL to load content from
url = "https://lilianweng.github.io/posts/2023-06-23-agent/"

# Fetch HTML content from the URL
response = requests.get(url)
html_content = response.content.decode("utf-8")

# Create a Document object with the HTML content and metadata
doc = Document(page_content=html_content, metadata={"source": url})
documents = [doc]

# Initialize the BeautifulSoupTransformer
bs_transformer = BeautifulSoupTransformer()

# Specify the tags to extract

tags_to_extract = ["p", "h1", "h2", "h3","h4","h5","h6", "ul", "ol", "table"]
# Transform the documents
docs_transformed = bs_transformer.transform_documents(documents, tags_to_extract=tags_to_extract)

# Print the transformed content
for transformed_doc in docs_transformed:
    print(transformed_doc)
