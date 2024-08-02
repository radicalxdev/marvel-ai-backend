from pydantic import BaseModel
from typing import Optional, List, Any
from enum import Enum
from services.tool_registry import BaseTool

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


class SyllabusGeneratorArgsModel(BaseModel):
    subject_topic: str
    grade_level: str
    subject: str
    course_description: str
    course_objectives: str
    required_materials: str
    grading_policy: str
    course_outline: str
    class_policies: str
    instructor_name: str
    instructor_title: str
    important_dates: Optional[str] = None
    learning_outcomes: Optional[str] = None
    class_schedule: Optional[str] = None
    instructor_contact: Optional[str] = None
    additional_customizations: Optional[str] = None
