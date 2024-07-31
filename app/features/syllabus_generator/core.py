from app.services.logger import setup_logger
from app.features.syllabus_generator.tools import SyllabusRequestArgs, generate_syllabus
from app.api.error_utilities import SyllabusGeneratorError
from app.services.schemas import SyllabusGeneratorArgsModel

logger = setup_logger(__name__)

def executor(syllabus_args: SyllabusGeneratorArgsModel, verbose: bool = True):
    if verbose:
        logger.info(f"File URL loaded: {syllabus_args.file_url}")

    try:
        request_args = SyllabusRequestArgs(**syllabus_args.dict(exclude_unset=True))
        syllabus = generate_syllabus(request_args, verbose=verbose)
    except Exception as e:
        logger.error(f"Failed to generate syllabus: {str(e)}")
        raise SyllabusGeneratorError(f"Failed to generate syllabus: {str(e)}") from e

    return syllabus