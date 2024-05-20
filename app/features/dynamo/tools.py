from langchain_community.document_loaders import YoutubeLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.prompts import PromptTemplate
from langchain_google_vertexai import VertexAI
from langchain_core.output_parsers import JsonOutputParser
from langchain.chains.summarize import load_summarize_chain
from langchain_core.pydantic_v1 import BaseModel, Field
from services.logger import setup_logger
import os


logger = setup_logger(__name__)

# AI Model
model = VertexAI(model="gemini-1.0-pro")

def read_text_file(file_path):
    # Get the directory containing the script file
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Combine the script directory with the relative file path
    absolute_file_path = os.path.join(script_dir, file_path)
    
    with open(absolute_file_path, 'r') as file:
        return file.read()

# Summarize chain
def summarize_transcript(youtube_url: str, max_video_length=600, verbose=False) -> str:
    loader = YoutubeLoader.from_youtube_url(youtube_url, add_video_info=True)
    splitter = RecursiveCharacterTextSplitter(
        chunk_size = 1000,
        chunk_overlap = 0
    )
    docs = loader.load()
    split_docs = splitter.split_documents(docs)
    
    if not docs:
        raise ValueError("No documents found")

    length = docs[0].metadata["length"]
    title = docs[0].metadata["title"]

    if length > max_video_length:
        raise ValueError(f"Video is too long, please provide a video less than {max_video_length} seconds long")

    if verbose:
        logger.info(f"Found video with title: {title} and length: {length}")
        logger.info(f"Splitting documents into {len(split_docs)} chunks")
    
    chain = load_summarize_chain(model, chain_type='map_reduce')
    response = chain(split_docs)
    
    if response and verbose: logger.info("Successfully completed generating summary")
    
    return response

def generate_flashcards(summary: str, verbose=False) -> list:
    # Receive the summary from the map reduce chain and generate flashcards
    parser = JsonOutputParser(pydantic_object=Flashcard)
    
    if verbose: logger.info(f"Beginning to process summary")
    
    template = read_text_file("prompt/dynamo-prompt.txt")
    examples = read_text_file("prompt/examples.txt")
    
    prompt = PromptTemplate(
        template=template,
        input_variables=["summary", "examples"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )
    
    chain = prompt | model | parser
    
    try:
        response = chain.invoke({"summary": summary, "examples": examples})
    except Exception as e:
        logger.error(f"Failed to generate flashcards: {e}")
        return []
    
    return response

class Flashcard(BaseModel):
    concept: str = Field(description="The concept of the flashcard")
    definition: str = Field(description="The definition of the flashcard")