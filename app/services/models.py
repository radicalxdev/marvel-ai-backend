from pydantic import BaseModel
from typing import Optional, List, Any
from pydantic import Field

class User(BaseModel):
    name: str
    email: str
    password: str
    
class Role(BaseModel):
    name: str
    description: str

class MessageType(BaseModel):
    name: str
    description: str

class MessagePayload(BaseModel):
    content: str

class Feature(BaseModel):
    name: str
    description: str

class Message(BaseModel):
  role: Role
  type: MessageType
  timestamp: Optional[Any] = None
  payload: Optional[Any] = None
    
class ChatRequest(BaseModel):
    user: User
    feature: Feature
    messages: Optional[List[Message]] = Field(default = None)
    
class ChatResponse(BaseModel):
    user: User
    feature: Feature
    messages: List[Message]