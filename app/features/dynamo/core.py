from fastapi import UploadFile
from app.services.logger import setup_logger
from app.api.error_utilities import VideoTranscriptError
from app.features.dynamo.tools import get_loader, summarize_transcript, generate_flashcards, summarize_documents

logger = setup_logger(__name__)

def executor(youtube_url: str = None, files: list[UploadFile] = None, verbose=False, max_flashcards=10):
    sanitized_flashcards = []

    if youtube_url:
        try:
            logger.info(f"Processing YouTube URL: {youtube_url}")
            summary = summarize_transcript(youtube_url, verbose=verbose)
            logger.info(f"Summary for YouTube URL: {summary}")
            flashcards = generate_flashcards(summary, max_flashcards=max_flashcards, verbose=verbose)
            for flashcard in flashcards:
                if 'concept' in flashcard and 'definition' in flashcard:
                    sanitized_flashcards.append({
                        "concept": flashcard['concept'],
                        "definition": flashcard['definition']
                    })
                else:
                    logger.warning(f"Malformed flashcard skipped: {flashcard}")
        except VideoTranscriptError as e:
            logger.error(f"Error in processing YouTube URL -> {e}")
            raise ValueError(f"Error in processing YouTube URL: {e}")
        except Exception as e:
            logger.error(f"Error in executor: {e}")
            raise ValueError(f"Error in executor: {e}")

    if files:
        for file in files:
            try:
                logger.info(f"Processing file: {file.filename}")
                loader_class = get_loader(file)
                
                # 문서 로드
                loader = loader_class([file])
                documents = loader.load()
                logger.info(f"Documents loaded: {documents}")
                
                # 문서 요약
                summary = summarize_documents(documents)
                logger.info(f"Summary for file {file.filename}: {summary}")
                
                # 플래시카드 생성
                flashcards = generate_flashcards(summary, verbose=verbose, max_flashcards=max_flashcards)
                sanitized_flashcards.extend(flashcards[:max_flashcards])
            except Exception as e:
                logger.error(f"Error in processing {file.filename} -> {e}")
                raise ValueError(f"Error in processing {file.filename}: {e}")

    return sanitized_flashcards

