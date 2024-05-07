from fastapi import APIRouter
from langchain_google_vertexai import VertexAI

router = APIRouter()

@router.get("/")
def read_root():
    return {"Hello": "World"}

@router.post("/test-gcp")
def test_llm(request: str):
    model = VertexAI(model_name="gemini-1.0-pro")
    message = request
    response = model.invoke(message)
    return {"message": response}