from typing import List
from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.chains.summarize.chain import load_summarize_chain

class NotesGeneratorPipeline:
    """
    A pipeline for generating notes using a retrieval-based approach 
    plus a generative LLM (Google Gemini).
    """

    def __init__(
        self,
        doc_url: str = "",
        doc_type: str = "",
        text_content: str = "",
        focus_topic: str = "",
        lang: str= "en"
    ):
        self.doc_url = doc_url
        self.doc_type = doc_type
        self.text_content = text_content
        self.focus_topic = focus_topic or "General"
        self.lang = lang

        # Initialize the LLM (Google Gemini) for text generation
        self.model = ChatGoogleGenerativeAI(model="gemini-1.5-pro")
        # Initialize embeddings for Chroma
        self.embedding_model = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        self.vectorstore = None
        self.retriever = None

    def generate_notes(self, docs: List[Document]) -> str:
        """
        Generate notes from the provided documents using a summarization approach.
        If documents exist, we build a vector store + retrieval pipeline. 
        If no documents, we do a direct LLM call with minimal context.
        """
        # If no docs and no text_content, nothing to summarize
        if not docs and not self.text_content:
            return "No documents or text content provided."
        
        # If we have documents, build a vector store and summarize
        doc_summary = ""
        if docs:
            # 1. Build a vectorstore from docs
            self.vectorstore = Chroma.from_documents(docs, self.embedding_model)
            self.retriever = self.vectorstore.as_retriever()

            # 2. Summarize the documents, focusing on the topic, text_content & language if needed
            # Here, we are using "map_reduce" chain for summarization (other options can be considered)
            summarize_chain = load_summarize_chain(self.model, chain_type="map_reduce")

            # Construct a "prompt" for the final summarization
            prompt_template = f"Summarize the content focusing on '{self.focus_topic}'. Language: {self.lang}"
            # I believe we can add a more advanced multi-step retrieval,

            doc_summary = summarize_chain.run({"input_documents": docs, "question": prompt_template})

        # If we also have text_content, or only text_content, do a direct LLM call
        text_summary = ""
        if self.text_content and not docs:
            # Summarize raw text alone
            text_summary = self.model.invoke(
                [f"Summarize this text focusing on '{self.focus_topic}' in {self.lang}:\n{self.text_content}"]
            )
        elif self.text_content and docs:
            # You can combine doc_summary + text_content if you want
            text_summary = self.model.invoke(
                [f"Additionally, consider this raw text focusing on '{self.focus_topic}' in {self.lang}:\n{self.text_content}"]
            )


        # Combine doc_summary and text_summary
        if doc_summary and text_summary:
            return doc_summary + "\n\n" + text_summary
        elif doc_summary:
            return doc_summary
        elif text_summary:
            return text_summary
        return "No content to summarize."