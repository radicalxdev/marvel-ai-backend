from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from typing import List
from services.gcp import setup_logger
from services.models import ChatRequest, ChatResponse
from utils.auth import key_check

logger = setup_logger()

router = APIRouter()

@router.get("/")
def read_root():
    return {"Hello": "World"}

@router.post("/test", response_model=ChatResponse)
async def test(data: ChatRequest, _ = Depends(key_check) ):
    return ChatResponse(data=data.messages)

@router.post("/test-quizzify")
async def test_quizzify(data: ChatRequest, _ = Depends(key_check)):
    import features.quizzify.core as quizzify
    
    if data.type == "tool":
        return HTTPException(status_code=400, detail="Invalid request type")
    
    inputs = data.tool.inputs
    topic = inputs.get("topic")
    num_questions = int(inputs.get("num_questions"))
    upload_files = inputs.get("upload_files")
    
    return quizzify.executor(upload_files, topic, num_questions)