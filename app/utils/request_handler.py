from fastapi import Form
from app.services.models import ChatRequest, Type


def validate_multipart_form_data(
    user_id: str = Form(...), 
    user_fullName: str = Form(...), 
    user_email: str = Form(...),
    type: Type = Form(...),
    tool_id: int = Form(None),
    topic: str = Form(None),
    num_questions: int = Form(None)
):
    
    tool_inputs = [{"name": "topic", "value": topic}, {"name": "num_questions", "value": num_questions}]
    chat_request = ChatRequest(
        user={"id": user_id, "fullName": user_fullName, "email": user_email},
        type=type,
        tool={"id": tool_id, "inputs": tool_inputs} if tool_id is not None else None
    )
    return chat_request