from typing import List
from langchain_community.document_loaders import WebBaseLoader
from services.tool_registry import ToolFile
from langchain_core.documents import Document
from services.logger import setup_logger
from api.error_utilities import LoaderError


logger = setup_logger(__name__)

class WebPageLoader:
    def __init__(self, web_urls: List[ToolFile]):
        self.web_urls = web_urls

    def load(self) -> List[Document]:
        documents = []
        for file in self.web_urls:
            try:
                loader = WebBaseLoader(file)
                if file.endswith("xml"):
                    loader.default_parser = "xml"
                docs = loader.load()
                documents.extend(docs)
            except Exception as e:
                logger.error(f"An error occurred while processing web page at {file}: {str(e)}")
                raise LoaderError(f"Error loading web page: {file}") from e
        return documents
