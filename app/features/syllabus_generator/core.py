from app.services.logger import setup_logger
from app.features.syllabus_generator.tools import SyllabusRequestArgs
from app.features.syllabus_generator.tools import generate_syllabus
from app.features.syllabus_generator.document_loaders import generate_summary_from_img, summarize_transcript_youtube_url, get_summary
from app.api.error_utilities import SyllabusGeneratorError
from app.services.schemas import SyllabusGeneratorArgsModel

logger = setup_logger()

def executor(syllabus_generator_args: SyllabusGeneratorArgsModel,
            verbose: bool = True):
    
    if verbose:
        logger.info(f"File URL loaded: {syllabus_generator_args.file_url}")
    
    try:
        
        if syllabus_generator_args.file_type == 'img':
            summary = generate_summary_from_img(syllabus_generator_args.file_url)
        elif syllabus_generator_args.file_type == 'youtube_url':
            summary = summarize_transcript_youtube_url(syllabus_generator_args.file_url, verbose=verbose)
        else:
            summary = get_summary(syllabus_generator_args.file_url, syllabus_generator_args.file_type, verbose=verbose)
    
        request_args = SyllabusRequestArgs(
                                syllabus_generator_args,
                                summary)
        
        syllabus = generate_syllabus(request_args, verbose=verbose)

    except Exception as e:
        logger.error(f"Failed to generate syllabus: {str(e)}")
        raise SyllabusGeneratorError(f"Failed to generate syllabus: {str(e)}") from e

    return syllabus
