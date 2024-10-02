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

class RubricGeneratorArgs(BaseModel):
    standard: str = Field(..., min_length=1, max_length=255, description="the learning standard or objective")
    point_scale: int = Field(..., description="Point scale for the rubric, must be between 1 and 10")
    grade_level: Literal["elementary", "middle", "high", "college", "professional"] = Field(..., description="Educational level to which the content is directed")
    file_type: str = Field(..., description="Type of file being handled, according to the defined enumeration")
    file_url: str = Field(..., description="URL or path of the file to be processed that has the assignment description")
    lang: Optional[str] = Field(..., description="Language in which the file or content is written")