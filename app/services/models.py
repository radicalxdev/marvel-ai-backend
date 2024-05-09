from pydantic import BaseModel
from typing import Optional, List, Any
from pydantic import Field
from enum import Enum

class User(BaseModel):
    name: str
    email: str
    password: str
    
class Role(str, Enum):
    user = "user"
    assistant = "assistant"

class MessageType(str, Enum):
    text = "text"
    image = "image"
    video = "video"
    file = "file"

class MessagePayload(BaseModel):
    content: str

class Tool(BaseModel):
    id: int
    name: str
    description: str

class Message(BaseModel):
  role: Role
  type: MessageType
  timestamp: Optional[Any] = None
  payload: Optional[Any] = None
    
class ChatRequest(BaseModel):
    user: User
    tool: Tool
    messages: Optional[List[Message]] = Field(default = None)
    
class ChatResponse(BaseModel):
    user: User
    feature: Tool
    messages: List[Message]