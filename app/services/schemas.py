from pydantic import BaseModel, Field
from typing import Optional, List, Any, Literal
from enum import Enum
from app.services.assistant_registry import AssistantInputs
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
    text: str | dict

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

class GenericAssistantRequest(BaseModel):
    assistant_inputs: AssistantInputs
    
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
    subject: str
    course_description: str
    objectives: str
    required_materials: str
    grading_policy: str
    policies_expectations: str
    course_outline: str
    additional_notes: str
    file_url: str
    file_type: str
    lang: Optional[str] = "en"
    
class AIResistantArgs(BaseModel):
    assignment: str = Field(..., max_length=255, description="The given assignment")
    grade_level: Literal["pre-k", "kindergarten", "elementary", "middle", "high", "university", "professional"] = Field(..., description="Educational level to which the content is directed")
    file_type: str = Field(..., description="Type of file being handled, according to the defined enumeration")
    file_url: str = Field(..., description="URL or path of the file to be processed")
    lang: str = Field(..., description="Language in which the file or content is written")
    
class ConnectWithThemArgs(BaseModel):
    grade_level: str = Field(..., description="The grade level the teacher is instructing.")
    task_description: str = Field(..., description="A brief description of the subject or topic the teacher is instructing.")
    students_description: str = Field(..., description="A description of the students including age group, interests, location, and any relevant cultural or social factors.")
    td_file_url: str 
    td_file_type: str 
    sd_file_url: str
    sd_file_type: str
    lang: str = Field(..., description="The language in which the subject is being taught.")

class PresentationGeneratorInput(BaseModel):
    grade_level: str
    n_slides: int
    topic: str
    objectives: str
    additional_comments: str
    objectives_file_url: str
    objectives_file_type: str
    ac_file_url: str
    ac_file_type: str
    lang: Optional[str] = "en"

class RubricGeneratorArgs(BaseModel):
    grade_level: Literal["pre-k", "kindergarten", "elementary", "middle", "high", "university", "professional"]
    point_scale: int
    objectives: str
    assignment_desc: str
    objectives_file_url: str
    objectives_file_type: str
    ad_file_url: str
    ad_file_type: str
    lang: Optional[str]

class LessonPlanGeneratorArgs(BaseModel):
    grade_level: str
    topic: str
    objectives: str
    additional_customization: str
    objectives_file_url: str
    objectives_file_type: str
    ac_file_url: str
    ac_file_type: str
    lang: Optional[str] = "en"

class WritingFeedbackGeneratorArgs(BaseModel):
    grade_level: str
    assignment_description: str
    criteria: str
    writing_to_review: str
    criteria_file_url: str
    criteria_file_type: str
    wtr_file_url: str
    wtr_file_type: str
    lang: Optional[str] = "en"

class NotesGeneratorArgs(BaseModel):
    topic: str = Field(..., description="Topic of the notes")
    details: str = Field(..., description="What should the notes talk about")
    nb_columns: int = Field(..., description="Number of columns for the key concept notes generated")
    orientation: Literal["landscape", "portrait"] = Field(..., description="Orientation of the notes document created")
    file_urls: str = Field(..., description="Comma-separated URLs or paths of the files to be processed")
    file_types: str = Field(..., description="Comma-separated file types corresponding to the provided URLs (e.g., pdf,gdoc,img,youtube_url)")
    langs: str = Field(..., description="Comma-separated languages for each file (e.g., en,fr,es)")


