from fastapi import APIRouter, UploadFile, File, Request, Depends
from typing import List
from services.gcp import setup_logger
from services.models import ChatRequest
from utils.auth import key_check

logger = setup_logger()

router = APIRouter()

@router.get("/")
def read_root():
    return {"Hello": "World"}

@router.post("/test")
async def test(data: ChatRequest, _ = Depends(key_check) ):
    return {"message": "success", "data": data.model_dump()}

@router.post("/test-quizzify")
async def test_quizzify(topic: str, num_questions: int, upload_files: List[UploadFile] = File(...)):
    import features.quizzify.core as quizzify
    
    return quizzify.executor(upload_files, topic, num_questions)