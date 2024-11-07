from pydantic import BaseModel, Field
from typing import Optional, List, Any, Literal
from enum import Enum
from app.services.tool_registry import BaseTool


class User(BaseModel):
    id: str
    fullName: str
    email: str
    
class Role(str, Enum):
    human = "human"
    ai = "ai"
    system = "system"

class MessageType(str, Enum):
    text = "text"
    image = "image"
    video = "video"
    file = "file"

class MessagePayload(BaseModel):
    text: str

class Message(BaseModel):
    role: Role
    type: MessageType
    timestamp: Optional[Any] = None
    payload: MessagePayload
    
class RequestType(str, Enum):
    chat = "chat"
    tool = "tool"

class GenericRequest(BaseModel):
    user: User
    type: RequestType
    
class ChatRequest(GenericRequest):
    messages: List[Message]
    
class ToolRequest(GenericRequest):
    tool_data: BaseTool
    
class ChatResponse(BaseModel):
    data: List[Message]

class ToolResponse(BaseModel):
    data: Any
    
class ChatMessage(BaseModel):
    role: str
    type: str
    text: str

class GivenFiles(BaseModel):
    file_type: str = Field(..., description="Type of file being handled")
    file_url: str = Field(..., description="URL or path of the file to be processed to retrieve the notes")
    lang: Optional[str] = Field(..., description="Language in which the file or content is written")

class NotesGeneratorArgs(BaseModel):
    nb_columns: int = Field(..., description="number of columns for the key concept notes generated")
    orientation: Literal["landscape", "portrait"] = Field(..., description="orientation of the notes document created")
    givenfileslist: List[GivenFiles] = Field(..., description="upload or specify the various inputs to retrive notes from")


