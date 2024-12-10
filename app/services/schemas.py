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

class NotesGeneratorArgs(BaseModel):
    topic: str = Field(..., description="Topic of the notes")
    details: str = Field(..., description="What should the notes talk about")
    nb_columns: int = Field(..., description="Number of columns for the key concept notes generated")
    orientation: Literal["landscape", "portrait"] = Field(..., description="Orientation of the notes document created")
    file_urls: str = Field(..., description="Comma-separated URLs or paths of the files to be processed")
    file_types: str = Field(..., description="Comma-separated file types corresponding to the provided URLs (e.g., pdf,gdoc,img,youtube_url)")
    langs: str = Field(..., description="Comma-separated languages for each file (e.g., en,fr,es)")

