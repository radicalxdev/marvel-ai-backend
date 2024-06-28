from langchain_google_vertexai import VertexAIEmbeddings

class EmbeddingClient:
    def __init__(self, model_name, project, location):
        # Initialize the VertexAIEmbeddings client with the given parameters
        self.client = VertexAIEmbeddings(model_name=model_name, project=project, location=location)

    def embed_query(self, query):
        """Uses the embedding client to retrieve embeddings for the given query."""
        vectors = self.client.embed_query(query)
        return vectors

    def embed_documents(self, documents):
        """Retrieve embeddings for multiple documents."""
        try:
            return self.client.embed_documents(documents)
        except AttributeError:
            # If embed_documents is not available, fall back to using embed_query for each document
            return [self.embed_query(doc) for doc in documents]

def main():
    # Example usage
    model_name = "textembedding-gecko@003"
    project = "task1-420716"
    location = "us-central1"

    embedding_client = EmbeddingClient(model_name, project, location)

    # Example: Embed a single query
    query = "Hello, world!"
    query_embedding = embedding_client.embed_query(query)
    print(f"Embedding for '{query}':")
    print(query_embedding)

    # Example: Embed multiple documents
    documents = [
        "This is the first document.",
        "Here's the second document.",
        "And this is the third one."
    ]
    document_embeddings = embedding_client.embed_documents(documents)
    if document_embeddings:
        print("\nEmbeddings for multiple documents:")
        for i, embedding in enumerate(document_embeddings):
            print(f"Document {i+1}: {embedding[:5]}...") # Print first 5 elements of each embedding

if __name__ == "__main__":
    main()