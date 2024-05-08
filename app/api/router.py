from fastapi import APIRouter
from fastapi import UploadFile, File
from typing import List

router = APIRouter()

@router.get("/")
def read_root():
    return {"Hello": "World"}

@router.post("/test-quizzify")
async def test_quizzify(upload_files: List[UploadFile] = File(...)):
    import features.quizzify.core as quizzify
    
    return quizzify.executor(upload_files)