from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query, Form
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from typing import Union, List, Dict, Any, Optional
from app.services.schemas import ToolRequest, ChatRequest, Message, ChatResponse, ToolResponse
from app.utils.auth import key_check
from app.services.logger import setup_logger
from app.api.error_utilities import InputValidationError, ErrorResponse
from app.api.tool_utilities import load_tool_metadata, execute_tool, finalize_inputs
from app.features.dynamo.core import executor as dynamo_executor
import json

logger = setup_logger(__name__)
router = APIRouter()

@router.get("/")
def read_root():
    return {"Hello": "World"}

@router.post("/submit-tool", response_model=Union[ToolResponse, ErrorResponse])
async def submit_tool(
    data: Optional[str] = Form(""),
    youtube_url: str = Form(""),
    files: List[UploadFile] = File(None),
    max_flashcards: int = Query(10),
    _ = Depends(key_check)
):     
    try:
        result = {}

        if data:
            request_data = tool_request.tool_data
            requested_tool = load_tool_metadata(request_data.tool_id)
            request_inputs_dict = finalize_inputs(request_data.inputs, requested_tool['inputs'])
        
            result = execute_tool(request_data.tool_id, request_inputs_dict)
        
        # Handle additional features 
        if youtube_url or files:
            try:
                flashcards = dynamo_executor(youtube_url=youtube_url, files=files, verbose=True, max_flashcards=max_flashcards)
                result['flashcards'] = flashcards
            except Exception as e:
                logger.error(f"Error processing content: {e}")
                raise HTTPException(status_code=500, detail="Failed to process content.")
        
        return ToolResponse(data=result)
    
    except InputValidationError as e:
        logger.error(f"InputValidationError: {e}")
        return JSONResponse(
            status_code=400,
            content=jsonable_encoder(ErrorResponse(status=400, message=e.message))
        )
    
    except HTTPException as e:
        logger.error(f"HTTPException: {e}")
        return JSONResponse(
            status_code=e.status_code,
            content=jsonable_encoder(ErrorResponse(status=e.status_code, message=e.detail))
        )
    
    except Exception as e:
        logger.error(f"Error processing request: {e}")
        return JSONResponse(
            status_code=500,
            content=jsonable_encoder(ErrorResponse(status=500, message="Internal Server Error"))
        )

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, _ = Depends(key_check)):
    from app.features.Kaichat.core import executor as kaichat_executor
    
    user_name = request.user.fullName
    chat_messages = request.messages
    user_query = chat_messages[-1].payload.text
    
    response = kaichat_executor(user_name=user_name, user_query=user_query, messages=chat_messages)
    
    formatted_response = Message(
        role="ai",
        type="text",
        payload={"text": response}
    )
    
    return ChatResponse(data=[formatted_response]) 
