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
from bs4 import BeautifulSoup

load_dotenv()

class DocumentProcessor:
    def __init__(self):
        self.pages = []
        self.processed_urls = set()  # Set to store processed URLs

    def ingest_documents(self):
        st.header("Upload Documents/Media")

        # File uploader
        uploaded_files = st.file_uploader("Choose files", type=["pdf", "docx", "doc", "pptx", "ppt", "txt", "csv"], accept_multiple_files=True)

        # URL input
        urls = st.text_input("Enter URLs separated by comma")
        if urls:
            urls = urls.split(",")
            for url in urls:
                url = url.strip()
                if url and url not in self.processed_urls:  # Check if URL is not empty and already processed
                    self.process_url(url)

        if uploaded_files:
            for uploaded_file in uploaded_files:
                self.process_file(uploaded_file)

        if self.pages:
            st.write(f"Total pages/content processed: {len(self.pages)}")
            print(self.pages)
        else:
            st.write("No files or URLs processed.")

    def process_url(self, url):
        try:
            if "youtube.com" in url or "youtu.be" in url:
                video_id = self.extract_youtube_video_id(url)
                if video_id:
                    transcript = YouTubeTranscriptApi.get_transcript(video_id)
                    text = " ".join([entry["text"] for entry in transcript])
                    self.pages.append(text)
                else:
                    st.error("Could not extract video ID from URL.")
            else:
                # Fetch content from regular website URLs
                response = requests.get(url)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    text = soup.get_text(separator=' ')
                    self.pages.append(text)
                else:
                    st.error(f"Error fetching content from URL: {url}")

            self.processed_urls.add(url)  # Add URL to processed set
        except Exception as e:
            st.error(f"Error processing URL: {e}")

    def process_file(self, uploaded_file):
        file_extension = os.path.splitext(uploaded_file.name)[1].lower()
        unique_id = uuid.uuid4().hex
        original_name, _ = os.path.splitext(uploaded_file.name)
        temp_file_name = f"{original_name}_{unique_id}{file_extension}"
        temp_file_path = os.path.join(tempfile.gettempdir(), temp_file_name)

        with open(temp_file_path, 'wb') as f:
            f.write(uploaded_file.getvalue())

        if file_extension == ".pdf":
            loader = PyPDFLoader(temp_file_path)
        elif file_extension in [".docx", ".doc", ".pptx", ".ppt"]:
            loader = PyMuPDFLoader(temp_file_path)
        elif file_extension == ".txt":
            loader = TextLoader(temp_file_path)
        elif file_extension == ".csv":
            loader = CSVLoader(temp_file_path)
        else:
            loader = UnstructuredFileLoader(temp_file_path)

        self.pages.extend(loader.load())
        os.unlink(temp_file_path)

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
