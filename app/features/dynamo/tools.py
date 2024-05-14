from langchain_community.document_loaders import YoutubeLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.prompts import PromptTemplate
from langchain_google_vertexai import VertexAI
from langchain_core.output_parsers import JsonOutputParser
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
    
    return splitter.split_documents(docs)

# Num sampler
def find_key_concepts(documents: list, sample_size: int = 5):
    """Iterate through all documents of group size N and find key concepts"""
    if sample_size > len(documents):
        sample_size = len(documents) // 5
    
    num_docs_per_group = len(documents) // sample_size + (len(documents) % sample_size > 0)
    
    if num_docs_per_group > 5:
        num_docs_per_group = 3 # Default to 6 if too many documents
        print(f"Number of documents per group is too large. Defaulting to {num_docs_per_group}")
    
    groups = [documents[i:i + num_docs_per_group] for i in range(0, len(documents), num_docs_per_group)]
    
    parser = JsonOutputParser(pydantic_object=Flashcard)
    
    batch_concept = []
    
    print(f"Beginning to process {len(groups)} groups")
    for group in groups:
        group_content = ""
        
        for doc in group:
            group_content += doc.page_content
        
            prompt = PromptTemplate(
                template = """
                You are a student a text for your exam. Consider the following transcript from a video and find the core idea or concept along with a definition. This will be used to create a flashcard to help you study. You must provide a definition for the concept. Follow the format instructions provided.
                
                Transcript:
                -------------------------------
                {text}
                
                Instructions:
                -------------------------------
                {format_instructions}
                
                Respond only with JSON with the concept and definition.
                """,
                input_variables=["text"],
                partial_variables={"format_instructions": parser.get_format_instructions()}
            )

            # Create Chain
            chain = prompt | model | parser
            
            # Run Chain
            output_concept = chain.invoke({"text": group_content})
            
            print(f"Output concept: {output_concept}\n")
            
            batch_concept.append(output_concept)
            
    return batch_concept

class Flashcard(BaseModel):
    concept: str = Field(description="The concept or term")
    definition: str = Field(description="The summarized definition of the concept or term")