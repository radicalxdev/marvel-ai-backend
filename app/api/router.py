from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from typing import Union
from services.schemas import ToolRequest, ChatRequest, Message, ChatResponse, ToolResponse
from utils.auth import key_check
from services.logger import setup_logger
from api.error_utilities import InputValidationError, ErrorResponse
from api.tool_utilities import load_tool_metadata, execute_tool, finalize_inputs

logger = setup_logger(__name__)
router = APIRouter()

@router.get("/")
def read_root():
    return {"Hello": "World"}

@router.post("/submit-tool", response_model=Union[ToolResponse, ErrorResponse])
async def submit_tool( data: ToolRequest, _ = Depends(key_check)):     
    try: 
        # Unpack GenericRequest for tool data
        request_data = data.tool_data
        
        requested_tool = load_tool_metadata(request_data.tool_id)
        
        request_inputs_dict = finalize_inputs(request_data.inputs, requested_tool['inputs'])

        result = execute_tool(request_data.tool_id, request_inputs_dict)
        
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

@router.post("/chat", response_model=ChatResponse)
async def chat( request: ChatRequest, _ = Depends(key_check) ):
    from features.Kaichat.core import executor as kaichat_executor
    
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