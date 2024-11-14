import os
from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from typing import Union
from app.services.schemas import ToolRequest, ChatRequest, Message, ChatResponse, ToolResponse
from app.utils.auth import key_check
from app.services.logger import setup_logger
from app.api.error_utilities import InputValidationError, ErrorResponse
from app.api.tool_utilities import load_tool_metadata, execute_tool, finalize_inputs
from fastapi.responses import FileResponse
from starlette.background import BackgroundTask

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
        logger.info(f"GO TO FINALIZE_INPUTS, request_data.inputs: {request_data.inputs}")
        request_inputs_dict = finalize_inputs(request_data.inputs, requested_tool['inputs'])
        logger.info(f"GO TO EXECUTE_TOOL, request_inputs_dict: {request_inputs_dict}")
        result = execute_tool(request_data.tool_id, request_inputs_dict)

        logger.info(f"absolute_path_to_result: {os.path.abspath(result)}")

        # Check if the file exists
        if not os.path.exists(result):
            raise HTTPException(status_code=404, detail="PDF file not found")
        
        return FileResponse(
            path=result, 
            media_type='application/pdf', 
            filename="Notes.pdf",
            background=BackgroundTask(lambda: os.remove(result))
        )
    
    
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