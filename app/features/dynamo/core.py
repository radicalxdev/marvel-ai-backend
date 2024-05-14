from features.dynamo.tools import find_key_concepts, retrieve_youtube_documents

def executor(youtube_url: str):
    yt_documents = retrieve_youtube_documents(youtube_url)
    concepts = find_key_concepts(yt_documents)
    
    return concepts