from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Request
from services.schemas import GenericRequest, ChatResponse
from dependencies import get_db
from utils.auth import key_check
from utils.request_handler import validate_multipart_form_data
from services.firestore import get_data
from services.tool_registry import validate_inputs
import json


router = APIRouter()

@router.get("/")
def read_root():
    return {"Hello": "World"}

async def get_files(request: Request):
    form = await request.form()
    files = form.getlist("files")
    valid_files = [file for file in files if file != '']
    return valid_files

@router.post("/submit-tool")
async def submit_tool(
    data: str = Form(...), # Must be a string for incoming stringified request
    files: list[UploadFile] = Depends(get_files),
    db = Depends(get_db),
    _ = Depends(key_check)
):  
    try:
        # Convert stringified JSON to dictionary
        request_dict = json.loads(data)
        
        # Create Pydantic Model Instance
        request = GenericRequest(**request_dict)
        
        # Unpack GenericRequest for tool data
        request_data = request.tool_data
    
        requested_tool = get_data(db, "tools", str(request_data.tool_id)) # Tools registry has IDs as strings
        if requested_tool is None:
            raise HTTPException(status_code=404, detail="Tool not found")
        
        inputs = requested_tool['inputs']    
        request_inputs_dict = {input.name: input.value for input in request_data.inputs}
        
        if not validate_inputs(request_inputs_dict, inputs):
            raise HTTPException(status_code=400, detail="Input validation failed")
    
        # Files received
        print(f"Files received: {len(files)}")
        
        
        #TODO: Route according to requested tool
    
        return {"message": "success", "files": len(files)}
    
    
    except json.JSONDecodeError as e:
        print(f"JSON Decoding error: {str(e)}")
        raise HTTPException(status_code=400, detail=f"JSON Decoding error: {str(e)}")
    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/chat", response_model=ChatResponse)
async def chat(request: GenericRequest, _ = Depends(key_check)):
    from features.Kaichat.core import generate_response, get_conversation_history, update_conversation_history
    from features.Kaichat.kai_prompt import generate_kai_prompt
    
    user_id = request.user.id
    user_name = request.user.fullName
    user_query = request.messages[-1].payload.text 

    # Retrieve the user's conversation history
    history = get_conversation_history(user_id)

    # Generate a prompt based on the current query and conversation history
    prompt = generate_kai_prompt(user_query, history)

    # Generate the response from KAI
    response_text = generate_response(prompt)  # Ensure your generate_response accepts a prompt and handles it correctly

    # Update conversation history with the new interaction
    update_conversation_history(user_id, user_query, response_text)

    # Prepare the response to return
    return {"response": response_text}

