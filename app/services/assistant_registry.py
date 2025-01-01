from enum import Enum
from typing import Any, List, Optional, Union
from pydantic import BaseModel

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
    text: Union[str, dict]

class Message(BaseModel):
    role: Role
    type: MessageType
    timestamp: Optional[Any] = None
    payload: MessagePayload
    
class UserInfo(BaseModel):
    user_name: str
    user_age: int
    user_preference: str

class AssistantInputs(BaseModel):
    assistant_group: str
    assistant_name: str
    user_info: UserInfo
    messages: List[Message]