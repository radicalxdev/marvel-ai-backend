from app.services.logger import setup_logger
from app.api.error_utilities import LoaderError, ToolExecutorError
from app.services.schemas import NotesGeneratorArgs, GivenFiles
from app.features.notes_generator.document_loaders import get_docs
from app.features.notes_generator.tools import NotesGenerator
from typing import List
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = setup_logger()

def process_file(input_file: GivenFiles, verbose=True):
    """Process an individual file to retrieve documents."""
    try:
        if verbose: 
            logger.info(f"Processing File URL: {input_file.file_url}")
            logger.info(f"Generating docs from {input_file.file_type}")  
        docs = get_docs(input_file.file_url, input_file.file_type, verbose=True)
        return docs
    except Exception as e:
        logger.error(f"Failed to process file {input_file.file_url}: {e}")
        return []

def process_all_filesinputs(notes_generator_args: NotesGeneratorArgs) -> List:
    """Process all files in the input list concurrently and return a combined list of documents."""
    all_docs = []
    with ThreadPoolExecutor() as thread_pool:
        futures = [thread_pool.submit(process_file, input_file) for input_file in notes_generator_args.givenfileslist]
        
        for future in as_completed(futures):
            docs = future.result()
            all_docs.extend(docs)  # Add each file's documents to the combined list

    return all_docs

def executor(notes_generator_args: NotesGeneratorArgs, verbose=False):
    try:
        if verbose: 
            logger.info(f"Args = notes_generator_args: {notes_generator_args}")

        docs = process_all_filesinputs(notes_generator_args) 
         
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
