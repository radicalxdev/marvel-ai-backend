#import sys
#print(sys.executable)
#print(sys.path)
import streamlit as st
import os
import json
import tempfile
import uuid
from langchain_google_vertexai import VertexAIEmbeddings, VertexAI
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.document_loaders import (
    PyPDFLoader,
    UnstructuredWordDocumentLoader,
    UnstructuredExcelLoader,
    UnstructuredHTMLLoader,
    UnstructuredPowerPointLoader,
    UnstructuredCSVLoader,
)
from langchain_core.documents import Document
import google.auth
from PIL import Image
import pytesseract
import torchaudio
from moviepy.editor import VideoFileClip
import speech_recognition as sr
#print("SpeechRecognition imported successfully")

from pydub import AudioSegment

# Set the path to the service account key
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/home/sanjana3014/kai-ai-backend_/local-auth.json"  # Ensure this is the correct path


class DocumentProcessor:
    def __init__(self):
        self.pages = []  # List to keep track of pages from all documents

    def read_image(self, file_path):
        image = Image.open(file_path)
        text = pytesseract.image_to_string(image)
        return text

    def read_audio(self, file_path):
        if file_path.endswith(".mp3"):
            audio = AudioSegment.from_mp3(file_path)
            wav_path = file_path.replace(".mp3", ".wav")
            audio.export(wav_path, format="wav")
            file_path = wav_path
        recognizer = sr.Recognizer()
        with sr.AudioFile(file_path) as source:
            audio = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio)
            return text
        except sr.UnknownValueError:
            return "Could not understand the audio"
        except sr.RequestError as e:
            return f"Could not request results; {e}"

    def read_video(self, file_path):
        video = VideoFileClip(file_path)
        audio_path = os.path.join(tempfile.gettempdir(), f"{uuid.uuid4().hex}.wav")
        video.audio.write_audiofile(audio_path)
        text = self.read_audio(audio_path)
        os.remove(audio_path)
        return text
    
    def ingest_documents(self):
        uploaded_files = st.file_uploader("Upload files", type=['pdf', 'png', 'mp4', 'docx', 'xlsx', 'csv', 'pptx', 'html', 'jpg', 'jpeg', 'wav', 'mp3'], accept_multiple_files=True)
        
        if uploaded_files:
            for uploaded_file in uploaded_files:
                unique_id = uuid.uuid4().hex
                original_name, file_extension = os.path.splitext(uploaded_file.name)
                temp_file_name = f"{original_name}_{unique_id}{file_extension}"
                temp_file_path = os.path.join(tempfile.gettempdir(), temp_file_name)

                with open(temp_file_path, 'wb') as f:
                    f.write(uploaded_file.getvalue())

                if file_extension == ".pdf":
                    loader = PyPDFLoader(temp_file_path)
                    pages = loader.load()
                    self.pages.extend(pages)
                elif file_extension == ".docx":
                    loader = UnstructuredWordDocumentLoader(temp_file_path)
                    pages = loader.load()
                    self.pages.extend(pages)
                elif file_extension == ".xlsx":
                    loader = UnstructuredExcelLoader(temp_file_path)
                    pages = loader.load()
                    self.pages.extend(pages)
                elif file_extension == ".csv":
                    loader = UnstructuredCSVLoader(temp_file_path)
                    pages = loader.load()
                    self.pages.extend(pages)
                elif file_extension == ".pptx":
                    loader = UnstructuredPowerPointLoader(temp_file_path)
                    pages = loader.load()
                    self.pages.extend(pages)
                elif file_extension == ".html":
                    loader = UnstructuredHTMLLoader(temp_file_path)
                    pages = loader.load()
                    self.pages.extend(pages)
                elif file_extension in ['.jpg', '.jpeg', '.png']:
                    text = self.read_image(temp_file_path)
                    self.pages.append(Document(page_content=text, metadata={"source": temp_file_path}))
                elif file_extension in ['.wav', '.mp3']:
                    text = self.read_audio(temp_file_path)
                    self.pages.append(Document(page_content=text, metadata={"source": temp_file_path}))
                elif file_extension == ".mp4":
                    text = self.read_video(temp_file_path)
                    self.pages.append(Document(page_content=text, metadata={"source": temp_file_path}))
                else:
                    st.error(f"Unsupported file type: {file_extension}")
                    continue

                os.unlink(temp_file_path)
            
            st.success(f"Total pages processed: {len(self.pages)}")

class EmbeddingClient:
    def __init__(self, model_name, project, location):
        print("Initializing VertexAIEmbeddings client")
        try:
            credentials, _ = google.auth.default()
            self.client = VertexAIEmbeddings(
                model=model_name,
                project=project,
                location=location,
                credentials=credentials
            )
            print("VertexAIEmbeddings client initialized successfully")
        except Exception as e:
            print(f"Error initializing VertexAIEmbeddings client: {e}")
        
    def embed_query(self, query):
        print(f"Embedding query: {query}")
        try:
            vectors = self.client.embed_query(query)
            print(f"Embeddings retrieved: {vectors}")
            return vectors
        except Exception as e:
            print(f"Error embedding query: {e}")
            return None
    
    def embed_documents(self, documents):
        print(f"Embedding documents: {documents}")
        try:
            return self.client.embed_documents(documents)
        except Exception as e:
            print(f"Error embedding documents: {e}")
            return None

class ChromaCollectionCreator:
    def __init__(self, processor, embed_model):
        self.processor = processor
        self.embed_model = embed_model
        self.db = None
    
    def create_chroma_collection(self):
        if len(self.processor.pages) == 0:
            st.error("No documents found!", icon="🚨")
            return

        text_splitter = CharacterTextSplitter(
            separator="\n",
            chunk_size=1000,
            chunk_overlap=200
        )
        
        texts = text_splitter.split_documents(self.processor.pages)

        if texts:
            st.success(f"Successfully split pages into {len(texts)} text chunks!", icon="✅")
        else:
            st.error("Failed to split documents into chunks!", icon="🚨")
            return

        try:
            self.db = Chroma.from_documents(documents=texts, embedding=self.embed_model)
            st.success("Successfully created Chroma Collection!", icon="✅")
        except Exception as e:
            st.error(f"Failed to create Chroma Collection! Error: {e}", icon="🚨")
    
    def query_chroma_collection(self, query):
        if self.db:
            docs = self.db.similarity_search_with_relevance_scores(query)
            if docs:
                return docs[0]
            else:
                st.error("No matching documents found!", icon="🚨")
        else:
            st.error("Chroma Collection has not been created!", icon="🚨")

class QuizGenerator:
    def __init__(self, topic=None, num_questions=1, vectorstore=None):
        self.topic = topic if topic else "General Knowledge"
        if num_questions > 10:
            raise ValueError("Number of questions cannot exceed 10.")
        self.num_questions = num_questions
        self.vectorstore = vectorstore
        self.llm = None
        self.question_bank = []
        self.system_template = """
            You are a subject matter expert on the topic: {topic}
            
            Follow the instructions to create a quiz question:
            1. Generate a question based on the topic provided and context as key "question"
            2. Provide 4 multiple choice answers to the question as a list of key-value pairs "choices"
            3. Provide the correct answer for the question from the list of answers as key "answer"
            4. Provide an explanation as to why the answer is correct as key "explanation"
            
            You must respond as a JSON object with the following structure:
            {{
                "question": "<question>",
                "choices": [
                    {{"key": "A", "value": "<choice>"}},
                    {{"key": "B", "value": "<choice>"}},
                    {{"key": "C", "value": "<choice>"}},
                    {{"key": "D", "value": "<choice>"}}
                ],
                "answer": "<answer key from choices list>",
                "explanation": "<explanation as to why the answer is correct>"
            }}
            
            Context: {context}
            """
    
    def init_llm(self):
        self.llm = VertexAI(
            model_name="gemini-pro",
            temperature=0.8,
            max_output_tokens=500
        )

    def generate_question_with_vectorstore(self):
        if not self.llm:
            self.init_llm()
        if not self.vectorstore:
            raise ValueError("Vectorstore not provided.")

        retriever = self.vectorstore.as_retriever()
        prompt = PromptTemplate.from_template(self.system_template)
        setup_and_retrieval = RunnableParallel(
            {"context": retriever, "topic": RunnablePassthrough()}
        )
        chain = setup_and_retrieval | prompt | self.llm
        response = chain.invoke(self.topic)
        return response

    def generate_quiz(self) -> list:
        self.question_bank = []
        unique_questions = set()
        retries = 0  # Counter to prevent infinite loops in case of repeated questions
        while len(self.question_bank) < self.num_questions and retries < self.num_questions * 2:
            try:
                question_str = self.generate_question_with_vectorstore()
                question = json.loads(question_str)
                question_text = question.get("question")
                if question_text and question_text not in unique_questions:
                    self.question_bank.append(question)
                    unique_questions.add(question_text)
                else:
                    print("Duplicate or invalid question detected.")
            except json.JSONDecodeError:
                print("Failed to decode question JSON.")
                continue
            retries += 1
        return self.question_bank

class QuizManager:
    def __init__(self, questions: list):
        self.questions = questions
        self.total_questions = len(questions)

    def get_question_at_index(self, index: int):
        return self.questions[index]

    def next_question_index(self, direction=1):
        current_index = st.session_state.get("question_index", 0)
        new_index = current_index + direction
        st.session_state["question_index"] = new_index

    def is_last_question(self):
        return st.session_state["question_index"] >= (self.total_questions - 1)

    def is_first_question(self):
        return st.session_state["question_index"] == 0