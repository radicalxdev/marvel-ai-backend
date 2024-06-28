import streamlit as st
from langchain_community.document_loaders import (
    PyPDFLoader,
    UnstructuredWordDocumentLoader,
    UnstructuredPowerPointLoader,
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
        self.processed_urls = set()  # Set to store processed URLs

    def ingest_documents(self):
        if 'convertButton' not in st.session_state:
            st.session_state.convertButton = 0
        st.header("Upload Documents/Media")

        fileTypes = ["pdf", "docx", "doc", "pptx", "ppt", "txt", "csv"]
        
        # File uploader
        uploaded_files = st.file_uploader("Choose files", type=fileTypes, accept_multiple_files=True)

        for files in uploaded_files:
            st.write("Specify any specific pages for " + files.name)

        # URL input
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

        st.write(st.session_state.convertButton)
        if uploaded_files:
            for uploaded_file in uploaded_files:
                self.process_file(uploaded_file, st.session_state.convertButton)
        
        if st.button("Convert to quiz"):
            st.session_state.convertButton = 1
            if self.pages:
                st.write(f"Total pages/content processed: {len(self.pages)}")
                for i, page in enumerate(self.pages):
                    st.write(f"Content {i + 1}:\n{page[:200]}...")  # Display a preview of each content
            elif not self.pages:
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

    def process_file(self, uploaded_file, isButton):
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
                ".docx": UnstructuredWordDocumentLoader,
                ".doc": UnstructuredWordDocumentLoader,
                ".pptx": UnstructuredPowerPointLoader,
                ".ppt": UnstructuredPowerPointLoader,
                ".txt": TextLoader,
                ".csv": CSVLoader
            }
            
            loader_class = loader_map.get(file_extension, UnstructuredFileLoader)
            loader = loader_class(temp_file_path)
            
            pages=[]
            pagesLoader = loader.load()
            pages.extend([page.page_content for page in pagesLoader])  # Standardize content type

            # Asks the user to select a range and accepts the numbers regardless of if there are too many
            # Checks for dashes, extra spaces, and out of order numbers
            st.write(f"Total pages/content in {uploaded_file.name}: {len(pages)}")
            page_numbers = st.text_input(
                "Specify which pages you'd like to keep from " + uploaded_file.name,
                placeholder="Ex: 1-4, 7, 9")
            page_numbers = page_numbers.replace(" ", "")
            page_numbers_formatted= page_numbers.split(",", maxsplit=-1)
            page_numbers_formatted.sort()
            for number in page_numbers_formatted:
                if number.__contains__("-"):
                    dashed_numbers= number.split("-", maxsplit=-1)
                    dashed_numbers.sort()
                    for num in range(int(dashed_numbers[0]), int(dashed_numbers[1])+1):
                        if num <= len(pages) and not self.pages.__contains__(pages[num]):
                            self.pages.append(pages[num])
                elif number:
                    array_num=int(number)
                    if array_num <= len(pages) and not self.pages.__contains__(pages[array_num]):
                            self.pages.append(pages[array_num])
                elif isButton and not page_numbers:
                    # if the button is pressed and there is no input pages it adds all pages
                    self.pages.clear()
                    self.pages.extend(pages)
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
