import streamlit as st
from langchain.document_loaders import (
    PyPDFLoader,
    TextLoader,
    CSVLoader,
    PyMuPDFLoader,
    UnstructuredFileLoader,
)
import os
import tempfile
import uuid
from dotenv import load_dotenv
from youtube_transcript_api import YouTubeTranscriptApi
import requests
from newspaper import Article
import validators

load_dotenv()

class DocumentProcessor:
    def __init__(self):
        self.pages = []
        self.processed_urls = set()

    def ingest_documents(self):
        st.header("Upload Documents/Media")

        uploaded_files = st.file_uploader("Choose files", type=["pdf", "docx", "doc", "pptx", "ppt", "txt", "csv"], accept_multiple_files=True)

        urls = st.text_input("Enter URLs separated by comma")
        if urls:
            urls = urls.split(",")
            for url in urls:
                url = url.strip()
                if url and url not in self.processed_urls:
                    if validators.url(url):
                        self.process_url(url)
                    else:
                        st.error(f"Invalid URL: {url}")

        if uploaded_files:
            for uploaded_file in uploaded_files:
                self.process_file(uploaded_file)

        if self.pages:
            st.write(f"Total pages/content processed: {len(self.pages)}")
            for i, page in enumerate(self.pages):
                st.write(f"Content {i + 1}:\n{page[:200]}...")  # Display a preview of each content
        else:
            st.write("No files or URLs processed.")

    def process_url(self, url):
        try:
            if "youtube.com" in url or "youtu.be" in url:
                video_id = self.extract_youtube_video_id(url)
                if video_id:
                    transcript = YouTubeTranscriptApi.get_transcript(video_id)
                    text = " ".join([entry["text"] for entry in transcript])
                else:
                    st.error(f"Could not extract video ID from URL: {url}")
                    return
            else:
                article = Article(url)
                article.download()
                article.parse()
                text = article.text

            self.processed_urls.add(url)
            st.success(f"Successfully processed URL: {url}")
            self.pages.append(text)  # Append the text to self.pages
        except Exception as e:
            st.error(f"Error processing URL {url}: {str(e)}")

    def process_file(self, uploaded_file):
        try:
            file_extension = os.path.splitext(uploaded_file.name)[1].lower()
            unique_id = uuid.uuid4().hex
            original_name, _ = os.path.splitext(uploaded_file.name)
            temp_file_name = f"{original_name}_{unique_id}{file_extension}"
            temp_file_path = os.path.join(tempfile.gettempdir(), temp_file_name)

            with open(temp_file_path, 'wb') as f:
                f.write(uploaded_file.getvalue())

            loader_map = {
                ".pdf": PyPDFLoader,
                ".docx": PyMuPDFLoader,
                ".doc": PyMuPDFLoader,
                ".pptx": PyMuPDFLoader,
                ".ppt": PyMuPDFLoader,
                ".txt": TextLoader,
                ".csv": CSVLoader
            }

            loader_class = loader_map.get(file_extension, UnstructuredFileLoader)
            loader = loader_class(temp_file_path)

            pages = loader.load()
            self.pages.extend([page.page_content for page in pages])  # Standardize content type
            os.unlink(temp_file_path)
            st.success(f"Successfully processed file: {uploaded_file.name}")
        except Exception as e:
            st.error(f"Error processing file {uploaded_file.name}: {str(e)}")

    @staticmethod
    def extract_youtube_video_id(url):
        if "youtube.com" in url:
            video_id = url.split("v=")[1].split("&")[0]
        elif "youtu.be" in url:
            video_id = url.split("/")[-1]
        else:
            video_id = None
        if video_id and "?" in video_id:
            video_id = video_id.split("?")[0]
        return video_id

if __name__ == "__main__":
    processor = DocumentProcessor()
    processor.ingest_documents()
