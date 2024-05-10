from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from typing import List
from app.services.gcp import setup_logger
from app.services.models import ChatRequest, ChatResponse, ToolResponse
from app.utils.auth import key_check
from app.utils.request_handler import validate_multipart_form_data

logger = setup_logger()

router = APIRouter()

@router.get("/")
def read_root():
    return {"Hello": "World"}

@router.post("/test/messages", response_model=ChatResponse)
async def test(data: ChatRequest, _ = Depends(key_check) ):
    total_messages = data.messages
    logger.info(f"Total messages: {len(total_messages)}")
    return ChatResponse(data=total_messages)

@router.post("/test/tools", response_model=ToolResponse)
async def test(data: ChatRequest, _ = Depends(key_check) ):
    return ToolResponse(data=data.tool)

@router.post("/test-quizzify")
async def test_quizzify(
    chat_request: ChatRequest = Depends(validate_multipart_form_data),
    request_files: List[UploadFile] = File(...),
    _ = Depends(key_check)
):
    from features.quizzify.core import executor
    
    if chat_request.tool is None:
        raise HTTPException(status_code=400, detail="Tool not provided")
    
    form_inputs = chat_request.tool.inputs
    
    # Extract topic from form inputs
    topic = next((input for input in form_inputs if input.name == "topic"), None).value
    # Extract number of questions from form inputs
    num_questions = next((input for input in form_inputs if input.name == "num_questions"), None).value
    
    if topic is None:
        raise HTTPException(status_code=400, detail="Topic not provided")
    if num_questions is None:
        raise HTTPException(status_code=400, detail="Number of questions not provided")
    if request_files is None:
        raise HTTPException(status_code=400, detail="File extraction found no files")
    
    return {
        "topic": topic,
        "num_questions": num_questions,
        "request_files": request_files
    }
    
    #return executor(request_files, topic, num_questions)
