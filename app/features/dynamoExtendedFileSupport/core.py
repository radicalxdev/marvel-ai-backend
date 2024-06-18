from services.logger import setup_logger
from features.dynamoExtendedFileSupport.tools import file_loader_map, gfile_loader_map
from utils.allowed_file_extensions import FileType, GFileType
from utils.extract_url_file_extension import get_file_extension

logger = setup_logger(__name__)

def executor(file_url: str, app_type: str, verbose=False):
    if (verbose):
        print(file_url)

    if(app_type=="1"):
        file_type = get_file_extension(file_url)

        try:
            file_loader = file_loader_map[FileType(file_type.lower())]
            file_loader(file_url)
        except KeyError:
            print(f"Unsupported file type: {file_type}")
    elif(app_type[0]=="2"):        
        try:
            file_loader = gfile_loader_map[GFileType(app_type[4:].lower())]
            file_loader(file_url)
        except KeyError:
            print(f"Error")