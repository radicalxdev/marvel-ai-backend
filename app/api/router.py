from fastapi import APIRouter, Depends, HTTPException
from services.schemas import ToolRequest, ChatRequest, Message, ChatResponse, ToolResponse
from utils.auth import key_check
from services.logger import setup_logger
from services.tool_registry import validate_inputs

from api.tool_utilities import load_tool_metadata, prepare_input_data, execute_tool

logger = setup_logger(__name__)
router = APIRouter()

@router.get("/")
def read_root():
    return {"Hello": "World"}

@router.post("/submit-tool", response_model=ToolResponse)
async def submit_tool( data: ToolRequest, _ = Depends(key_check)):      
    # Unpack GenericRequest for tool data
    request_data = data.tool_data
    
    requested_tool = load_tool_metadata(request_data.tool_id)
    request_inputs_dict = prepare_input_data(request_data)
    
    if not validate_inputs(request_inputs_dict, requested_tool['inputs']):
        logger.error(f"Input validation failed")
        logger.error(f"Inputs: {request_inputs_dict}")
        logger.error(f"Firestore inputs: {requested_tool['inputs']}")
        raise HTTPException(status_code=400, detail="Input validation failed")
    else:
        logger.info(f"Input validation passed")

    result = execute_tool(request_data.tool_id, request_inputs_dict)
    
    return ToolResponse(data=result)

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