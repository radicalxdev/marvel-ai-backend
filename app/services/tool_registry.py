from pydantic import BaseModel,validator
from app.services.logger import setup_logger
from typing import List, Any, Optional, Dict, Union
from app.api.error_utilities import InputValidationError


logger = setup_logger(__name__)

class ToolInput(BaseModel):
    # Input from incoming request typically represent HTML Form elements
    name: str
    value: Any
    # When passing "files", the value field is an object with file details as properties
    
# Base model for all tools
class BaseTool(BaseModel):
    tool_id: int  # Unique identifier for each tool,
    inputs: List[ToolInput]

class Choice(BaseModel):
    key : str
    value : str
    
class QuestionFile(BaseModel):
    question : str
    choices : List[Choice]
    answer: str
    explanation : str

class ResultFile(BaseModel):
    data: List[QuestionFile]

class ToolFile(BaseModel):
    filePath: Optional[str] = None
    url: str
    filename: Optional[str] = None
    section_start: Optional[Union[float, List[float]]] = 0
    section_end: Optional[Union[float, List[float]]] = None
    specific_list: Optional[List[int]] = None
    file_type: str # [pdf, doc, docx, ppt, pptx, txt, xlsx, csv, web_url, youtube]
    
    @validator('section_start', 'section_end', pre=True, always=True)
    def parse_section(cls, value):
        if isinstance(value, str):
            parts = value.split(',')
            if len(parts) == 1:
                return float(parts[0])
            else:
                return [float(part) for part in parts]
        return value
