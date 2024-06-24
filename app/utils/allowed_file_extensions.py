from enum import Enum

class FileType(Enum):
    PDF = 'pdf'
    CSV = 'csv'
    TXT = 'txt'
    MD = 'md'
    URL = "url"
    PPTX = 'pptx'
    DOCX = "docx"
    XLS = "xls"
    XLSX = "xlsx"
    XML = 'xml'

class GFileType(Enum):
    DOC = 'doc'
    SHEET = "sheet"
    SLIDE = "slide"
    PDF = 'pdf'