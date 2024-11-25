from pydantic import BaseModel, Field
from typing import Optional, List, Any
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

class QuizzifyArgs(BaseModel):
    topic: str
    n_questions: int
    file_url: str
    file_type: str
    lang: Optional[str] = "en"

class WorksheetQuestion(BaseModel):
    question_type: str
    number: int
    
class WorksheetQuestionModel(BaseModel):
    worksheet_question_list: List[WorksheetQuestion]

class WorksheetGeneratorArgs(BaseModel):
    grade_level: str
    topic: str
    worksheet_list: WorksheetQuestionModel
    file_url: str
    file_type: str
    lang: Optional[str] = "en"
    
class SyllabusGeneratorArgsModel(BaseModel):
    grade_level: str
    course: str
    instructor_name: str
    instructor_title: str
    unit_time: str
    unit_time_value: int
    start_date: str
    assessment_methods: str
    grading_scale: str
    file_url: str
    file_type: str
    lang: Optional[str] = "en"
    
class ConnectWithThemArgs(BaseModel):
    grade_level: str = Field(..., description="The grade level the teacher is instructing.")
    task_description: str = Field(..., description="A brief description of the subject or topic the teacher is instructing.")
    students_description: str = Field(..., description="A description of the students including age group, interests, location, and any relevant cultural or social factors.")
    file_url: str = Field(..., description="URL of any relevant file associated with the teaching material.")
    file_type: str = Field(..., description="The type of the file")
    lang: str = Field(..., description="The language in which the subject is being taught.")