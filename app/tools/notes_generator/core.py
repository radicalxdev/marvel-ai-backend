from typing import Optional, Dict
from app.api.error_utilities import FileHandlerError
from app.utils.document_loaders import get_docs
from app.tools.notes_generator.tools import NotesGeneratorPipeline
from app.services.logger import setup_logger

logger = setup_logger(__name__)

def executor(
    doc_url: Optional[str] = None,
    doc_type: Optional[str] = None,
    text_content: Optional[str] = None,
    focus_topic: Optional[str] = None,
    lang: Optional[str] = "en",
) -> Dict[str, str]:
    """
    Executor function for generating notes using a retrieval + generation pipeline.

    Args:
        doc_url (str): URL for the document to load.
        doc_type (str): The type of document (pdf, docx, csv, etc.).
        text_content (str): Plain text input if the user wants to pass text directly.
        focus_topic (str): Focus or topic for the notes generation.
        lang (str): Language code (e.g. 'en', 'es', 'fr', etc.) to guide multilingual generation.

    Returns:
        Dict[str, str]: Contains the status and generated notes.
    """
    SUPPORTED_DOC_TYPES = {"pdf","docx","csv","txt","md","pptx","xls","xlsx","gpdf"}

    try:
        logger.info("Notes generation started...")

        # Validate that at least one of doc_url or text_content is provided
        if not doc_url and not text_content:
            raise ValueError("Either 'doc_url' or 'text_content' must be provided.")

        # Validate that if doc_url is provided, doc_type must also be provided
        if doc_url and not doc_type:
            raise ValueError("If 'doc_url' is provided, 'doc_type' must also be provided.")

        # 1. Load documents from doc_url if provided and doc_type is supported
        docs = []
        if doc_url and doc_type:
            if not isinstance(doc_type, str) or doc_type not in SUPPORTED_DOC_TYPES:
                raise ValueError(f"Unsupported doc_type: {doc_type}. Must be one of {SUPPORTED_DOC_TYPES}.")
            try:
                docs = get_docs(doc_url, doc_type, verbose=True)  # get_docs function from document_loaders.py
            except FileHandlerError as fnf:
                logger.error(f"Failed to load docs from {doc_url}: {str(e)}")
                raise ValueError(f"Failed to load docs from {doc_url} - {str(e)}")

        # 2. If user gave raw text, we can wrap it into a single-document list
        if text_content:
            from langchain_core.documents import Document
            docs.append(Document(page_content=text_content))

        # 3. Run the pipeline to generate notes
        pipeline = NotesGeneratorPipeline(
            focus_topic=focus_topic,
            lang=lang
        )
        notes = pipeline.generate_notes(docs)

        logger.info("Notes generation completed successfully.")
        return {"status": "success", "notes": notes}

    except ValueError as ve:
        logger.error(f"ValueError during notes generation: {str(ve)}")
        return {"status": "error", "message": str(ve)}
    except FileNotFoundError as fnf:
        logger.error(f"FileNotFoundError: {str(fnf)}")
        return {"status": "error", "message": "File not found. Please check the doc_url or file path."}
    except Exception as e:
        logger.error(f"Unexpected error during notes generation: {str(e)}")
        return {"status": "error", "message": "An unexpected error occurred. Please try again."}