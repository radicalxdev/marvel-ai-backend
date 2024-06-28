
import sys
import os
sys.path.append(os.path.abspath('../../'))
import streamlit as st
from langchain_core.documents import Document
from langchain.text_splitter import CharacterTextSplitter
from tasks.task1.task1 import DocumentProcessor
from tasks.task2.task2 import EmbeddingClient
from langchain_community.vectorstores import Chroma

class ChromaCollectionCreator:
    def __init__(self):
        self.processor = DocumentProcessor()
        self.embed_model = EmbeddingClient(
            model_name="textembedding-gecko@003",
            project="task1-420716",
            location="us-central1"
        )
        self.db = None

    def create_chroma_collection(self):
        st.header("Create Chroma Collection")

        # Step 1: Ingest documents
        self.processor.ingest_documents()

        if len(self.processor.pages) == 0:
            st.error("No documents/URLs found!", icon="🚨")
            return

        # Step 2: Split documents into text chunks
        text_splitter = CharacterTextSplitter(separator="\n\n", chunk_size=1000, chunk_overlap=200)
        texts = self.processor.pages
        all_chunks = []

        for text in texts:
            # Ensure text is a string
            if not isinstance(text, str):
                st.warning("Skipping non-string content.")
                continue

            # Split text into smaller chunks
            chunks = text_splitter.split_text(text)
            all_chunks.extend(chunks)

        st.success(f"Successfully split pages to {len(all_chunks)} text chunks!", icon="✅")

        if not all_chunks:
            st.error("No valid text chunks to process.", icon="🚨")
            return

        # Step 3: Generate embeddings for all chunks
        try:
            embeddings = self.embed_model.embed_documents(all_chunks)
        except Exception as e:
            st.error(f"Error generating embeddings: {str(e)}", icon="🚨")
            return

        # Step 4: Create Document objects with embeddings
        documents = [
            Document(page_content=chunk, metadata={})
            for chunk, embedding in zip(all_chunks, embeddings)
        ]

        st.info(f"Created {len(documents)} document objects with embeddings.")

        # Step 5: Create the Chroma Collection
        try:
            # Specify the path where Chroma should store its database
            persist_directory = "chroma_storage"
            self.db = Chroma.from_documents(
                documents=documents,
                embedding=self.embed_model,
                persist_directory=persist_directory
            )
            st.success("Successfully created Chroma Collection!", icon="✅")
        except Exception as e:
            st.error(f"Failed to create Chroma Collection: {str(e)}", icon="🚨")

def main():
    creator = ChromaCollectionCreator()
    creator.create_chroma_collection()

if __name__ == "__main__":
    main()
