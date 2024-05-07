# Redis In-Memory VectorStore

class RedisVectorStore:
    """Redis In-Memory VectorStore"""
    def __init__(self, redis_url, index_name):
        self.redis_url = redis_url
        self.index_name = index_name

    def similarity_search_with_score(self, query, k=3, return_metadata=False):
        """Search for similar vectors"""
        pass


metadata = [
    {
        "user": "john",
        "age": 18,
        "job": "engineer",
        "credit_score": "high",
    },
    {
        "user": "derrick",
        "age": 45,
        "job": "doctor",
        "credit_score": "low",
    },
    {
        "user": "nancy",
        "age": 94,
        "job": "doctor",
        "credit_score": "high",
    },
    {
        "user": "tyler",
        "age": 100,
        "job": "engineer",
        "credit_score": "high",
    },
    {
        "user": "joe",
        "age": 35,
        "job": "dentist",
        "credit_score": "medium",
    },
]
texts = ["foo", "foo", "foo", "bar", "bar"]

from langchain_community.vectorstores.redis import Redis
from langchain_openai import OpenAIEmbeddings

embeddings = OpenAIEmbeddings()

redis_url = "redis://localhost:6379"

rds, keys = Redis.from_texts_return_keys(
    texts,
    embeddings,
    metadatas=metadata,
    redis_url=redis_url,
    index_name="users",
)

print(rds.index_name)

if __name__ == "__main__":
    
    print(f"Successfully Created Redis Index: {rds.index_name}")
    print(f"Keys: {keys}")
    
    query = "foo"
    results = rds.similarity_search_with_score(query, k=3, return_metadata=True)
    
    for result in results:
        print(f"Content: {result[0].page_content} --- Score: {result[1]}")
        
    # Cleanup Process
    Redis.delete(keys, redis_url=redis_url)
    
    # delete the indices too
    Redis.drop_index(
        index_name="users", delete_documents=True, redis_url=redis_url
    )
    Redis.drop_index(
        index_name="users_modified",
        delete_documents=True,
        redis_url=redis_url,
    )
    print(f"Successfully Deleted Redis Index: {rds.index_name}")