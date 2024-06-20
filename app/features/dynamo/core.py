from features.dynamo.tools import summarize_transcript, generate_flashcards
from services.logger import setup_logger
from api.error_utilities import VideoTranscriptError

logger = setup_logger(__name__)

def executor(youtube_url: str, verbose=False):
    summary = summarize_transcript(youtube_url, verbose=verbose)
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