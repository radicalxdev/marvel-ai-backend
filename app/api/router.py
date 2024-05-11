from fastapi import APIRouter, UploadFile, File, Request, Depends
from typing import List
from services.gcp import setup_logger
from services.models import ChatRequest
from utils.auth import key_check
from fastapi.responses import JSONResponse
from features.Kaichat.core import generate_response, get_conversation_history, update_conversation_history
from features.Kaichat.kai_prompt import generate_prompt
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

@router.post("/chat-with-kai")
async def chat_with_kai(request: ChatRequest, _ = Depends(key_check)):
    """
    Endpoint to interact with the KAI chatbot.
    """
    try:
        # Assuming 'user_name' and 'user_query' are parts of the ChatRequest
        user_id = request.user.id
        user_name = request.user.name
        user_query = request.messages[0].payload.content  # Assuming message payload contains the query

        # Retrieve the user's conversation history
        history = get_conversation_history(user_id)

        # Generate a prompt based on the current query and conversation history
        prompt = generate_prompt(user_query, history)

        # Generate the response from KAI
        response_text = generate_response(prompt)  # Ensure your generate_response accepts a prompt and handles it correctly

        # Update conversation history with the new interaction
        update_conversation_history(user_id, user_query, response_text)

        # Prepare the response to return
        return {"response": response_text}
    except Exception as e:
        logger.error(f"Failed to process chat with KAI: {str(e)}")
        

