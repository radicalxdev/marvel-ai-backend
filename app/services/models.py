from pydantic import BaseModel
from typing import Optional, List, Any
from pydantic import Field
from enum import Enum

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

class Input(BaseModel):
    name: str 
    value: Any 

class Tool(BaseModel):
    id: int
    inputs: List[Input]

class Message(BaseModel):
  role: Role
  type: MessageType
  timestamp: Optional[Any] = None
  payload: MessagePayload
    
class Type(str, Enum):
    chat = "chat"
    tool = "tool"

class ChatRequest(BaseModel): # make utility func
    user: User # if Tool, ensure a Tool prop is sent
    type: Type # If type is chat, validate the payload to ensure messages are present
    tool: Optional[Tool] = Field(default = None)
    messages: Optional[List[Message]] = Field(default = None)
    
class ChatResponse(BaseModel):
    data: List[Message]

class ToolResponse(BaseModel):
    data: Any