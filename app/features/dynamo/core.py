from app.features.dynamo.tools import summarize_transcript, generate_flashcards, load_documents, summarize_docs
from app.services.logger import setup_logger
from app.api.error_utilities import VideoTranscriptError
from app.services.tool_registry import ToolFile

logger = setup_logger(__name__)

def executor(youtube_url: str, files: list[ToolFile], verbose=False):
    # New method
    documents = load_documents(youtube_url, files)
    summary = summarize_docs(documents)

    # Previous method
    # summary = summarize_transcript(youtube_url, verbose=verbose)
    
    flashcards = generate_flashcards(summary)

    sanitized_flashcards = []
    for flashcard in flashcards:
        if 'concept' in flashcard and 'definition' in flashcard:
            sanitized_flashcards.append({
                "concept": flashcard['concept'],
                "definition": flashcard['definition']
            })
        else:
            logger.warning(f"Malformed flashcard skipped: {flashcard}")

    return sanitized_flashcards 