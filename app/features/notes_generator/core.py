from app.services.logger import setup_logger
from app.api.error_utilities import LoaderError, ToolExecutorError
from app.services.schemas import NotesGeneratorArgs
from app.features.notes_generator.document_loaders import get_docs
from app.features.notes_generator.tools import NotesGenerator
from typing import List
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = setup_logger()

def process_file(file_url: str, file_type: str, lang: str, verbose=True):
    """Process an individual file to retrieve documents."""
    try:
        if verbose: 
            logger.info(f"Processing File URL: {file_url}")
            logger.info(f"File Type: {file_type}")
            logger.info(f"Language: {lang}")
        
        docs = get_docs(file_url, file_type, lang, verbose=True)  
        
        logger.info(f"Docs generated successfully for {file_url}")
        return docs
    except Exception as e:
        logger.error(f"Failed to process file {file_url}: {e}")
        return []

def process_all_filesinputs(file_urls_list: List[str], file_types_list: List[str], langs_list: List[str]) -> List:
    """Process all files in the input list concurrently and return a combined list of documents."""
    all_docs = []
    with ThreadPoolExecutor() as thread_pool:
        # Create tasks for each file input
        futures = [
            thread_pool.submit(process_file, file_url, file_type, lang)
            for file_url, file_type, lang in zip(file_urls_list, file_types_list, langs_list)
        ]
        for future in as_completed(futures):
            docs = future.result()
            all_docs.extend(docs)  # Add each file's documents to the combined list
            logger.info(f"docs extended")  

    return all_docs

def executor(topic: str,
            details: str,
            nb_columns: int,
            orientation: str,
            file_urls: str,
            file_types: str,
            langs: str,
            verbose: bool = False):
    
    try:
        notes_generator_args = NotesGeneratorArgs(
            topic=topic,
            details=details,
            nb_columns=nb_columns,
            orientation=orientation,
            file_urls=file_urls,
            file_types=file_types,
            langs=langs,
        )
        if verbose: 
            logger.info(f"Args = notes_generator_args: {notes_generator_args}")

        file_urls_list = file_urls.split(",")
        file_types_list = file_types.split(",")
        langs_list = langs.split(",")
    
        if len(file_urls_list) != len(file_types_list) or len(file_urls_list) != len(langs_list):
            raise ValueError("The number of file URLs, file types, and languages must match.")


        docs = process_all_filesinputs(file_urls_list, file_types_list, langs_list) 
         
        output = NotesGenerator(args=notes_generator_args, verbose=verbose).create_notes(docs)
        
        logger.info(f"Notes generated successfully in a PDF file")
    
    except LoaderError as e:
        error_message = str(e)
        logger.error(f"Error in Notes Generator Pipeline -> {error_message}")
        raise ToolExecutorError(error_message)
    
    except Exception as e:
        error_message = f"Error in executor: {e}"
        logger.error(error_message)
        raise ValueError(error_message)
    
    return output
