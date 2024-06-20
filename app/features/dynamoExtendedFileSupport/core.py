from services.logger import setup_logger
from features.dynamoExtendedFileSupport.tools import file_loader_map, generate_concepts_from_img, gfile_loader_map
from utils.allowed_file_extensions import FileType, GFileType
from utils.extract_url_file_extension import get_file_extension
from api.error_utilities import FileHandlerError

logger = setup_logger(__name__)

def executor(file_url: str, app_type: str, verbose=True):
    if (verbose):
        logger.info(f"File URL loaded: {file_url}")

    if(app_type=="1"):
        file_type = get_file_extension(file_url)
        try:
            file_loader = file_loader_map[FileType(file_type.lower())]
            file_loader(file_url, verbose)
        except Exception as e:
            logger.error(f"Unsupported file type: {file_type}")
            raise FileHandlerError(f"Unsupported file type", file_url) from e
    elif (app_type[0]=="2"):
        try:
            file_loader = file_loader_map[FileType(app_type[4:].lower())]
            file_loader(file_url, verbose)
        except Exception as e:
            logger.error(f"Invalid URL: {file_url}")
            raise FileHandlerError(f"Invalid URL", file_url) from e
    elif(app_type[0]=="3"):        
        try:
            file_loader = gfile_loader_map[GFileType(app_type[4:].lower())]
            file_loader(file_url, verbose)
        except Exception as e:
            logger.error(f"Unsupported file type for Google Drive")
            raise FileHandlerError(f"Unsupported file type for Google Drive", file_url) from e
    elif(app_type=="4"):
        return generate_concepts_from_img(file_url)