from typing import Optional, List
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
        focus_topic: Optional[str] = None,
        lang: Optional[str] = "en",
    ):
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
        if not docs:
            return "No documents provided."

        # 1. Build a vectorstore from docs
        self.vectorstore = Chroma.from_documents(docs, self.embedding_model)
        self.retriever = self.vectorstore.as_retriever()

        # 2. Summarize the documents, focusing on the topic & language if needed
        # Here, we are using "map_reduce" chain for summarization (other options can be considered)
        summarize_chain = load_summarize_chain(self.model, chain_type="map_reduce")

        # Construct a "prompt" for the final summarization
        prompt_template = f"Summarize the content focusing on '{self.focus_topic}'. Language: {self.lang}"
        # I believe we can add a more advanced multi-step retrieval, 

        # 3. Run the chain
        # For a "map_reduce" chain, we pass the docs plus any additional prompt as 'question'.
        result = summarize_chain.run({"input_documents": docs, "question": prompt_template})

        return result