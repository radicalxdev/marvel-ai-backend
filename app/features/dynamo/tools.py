from langchain_community.document_loaders import YoutubeLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.prompts import PromptTemplate
from langchain_google_vertexai import VertexAI
from langchain_core.output_parsers import JsonOutputParser
from services.gcp import read_blob_to_string
from pydantic import BaseModel, Field

# AI Model
model = VertexAI(model="gemini-1.0-pro")

# Youtube Loader # Chunk and Splitter
def retrieve_youtube_documents(youtube_url: str):
    """Retrieve youtbe transcript and create a list of documents"""
    loader = YoutubeLoader.from_youtube_url(youtube_url, add_video_info=True)
    splitter = RecursiveCharacterTextSplitter(
        chunk_size = 1000,
        chunk_overlap = 0
    )
    
    docs = loader.load()
    
    length = docs[0].metadata["length"]
    title = docs[0].metadata["title"]
    
    print(f"Found video with title: {title} and length: {length}")
    
    # If docs empty, throw error
    if not docs:
        raise ValueError("No documents found")
    
    # if docs too long, throw error
    if length > 1200: # 20 minutes
        raise ValueError("Video too long")
    
    return splitter.split_documents(docs)
        

# Num sampler
def find_key_concepts(documents: list, sample_size: int = 6):
    """Iterate through all documents of group size N and find key concepts"""
    if sample_size > len(documents):
        sample_size = len(documents) // 5
    
    num_docs_per_group = len(documents) // sample_size + (len(documents) % sample_size > 0)
    
    if num_docs_per_group > 5:
        num_docs_per_group = 6 # Default to 6 if too many documents
        print(f"Number of documents per group is too large. Defaulting to {num_docs_per_group}")
    
    groups = [documents[i:i + num_docs_per_group] for i in range(0, len(documents), num_docs_per_group)]
    
    parser = JsonOutputParser(pydantic_object=Flashcard)
    
    batch_concept = []
    
    print(f"Beginning to process {len(groups)} groups")
    
    template = read_blob_to_string(bucket_name="backend-prompt-lib", file_path="dynamo/05142024-dynamo-prompt.txt")
    prompt = PromptTemplate(
                template = template,
                input_variables=["text"],
                partial_variables={"format_instructions": parser.get_format_instructions()}
            )
    # Create Chain
    chain = prompt | model | parser
    
    for group in groups:
        group_content = ""
        
        for doc in group:
            group_content += doc.page_content

            # Run Chain
            output_concept = chain.invoke({"text": group_content})
            
            print(f"Output concept: {output_concept}\n")
            
            batch_concept.append(output_concept)
            
    return batch_concept

class Flashcard(BaseModel):
    concept: str = Field(description="The concept or term")
    definition: str = Field(description="The summarized definition of the concept or term")