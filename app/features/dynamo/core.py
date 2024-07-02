from app.services.logger import setup_logger
from features.dynamo.tools import get_summary, summarize_transcript_youtube_url, generate_flashcards, generate_concepts_from_img

logger = setup_logger(__name__)

def executor(file_url: str, file_type: str, verbose=True):
    if (verbose):
        logger.info(f"File URL loaded: {file_url}")
    flashcards = []

    if file_type == "img":
        flashcards = generate_concepts_from_img(file_url)
    elif (file_type == 'youtube_url'):
        summary = summarize_transcript_youtube_url(file_url, verbose=verbose)
        flashcards = generate_flashcards(summary, verbose)
    else:
        summary = get_summary(file_url, file_type, verbose=verbose)
        flashcards = generate_flashcards(summary, verbose)


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