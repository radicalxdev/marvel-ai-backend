from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Request
from services.schemas import GenericRequest, ChatResponse, ToolResponse
from typing import List
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

@router.post("/test-dynamo")
async def test_dynamo(
    chat_request: GenericRequest,
    #_ = Depends(key_check)
):
    from features.dynamo.tools import retrieve_youtube_documents, find_key_concepts
    
    if chat_request.tool_data is None:
        raise HTTPException(status_code=400, detail="Tool not provided")
    
    form_inputs = chat_request.tool_data.inputs
    
    # Extract youtube url from form inputs
    url = next((input for input in form_inputs if input.name == "youtube_url"), None).value
    
    if url is None:
        raise HTTPException(status_code=400, detail="Youtube URL not provided")
    
    yt_documents = retrieve_youtube_documents(url)
    #try:
    #    concepts = find_key_concepts(yt_documents)
    #except Exception as e:
    #    print(f"Model error: {str(e)}")
    #    raise HTTPException(status_code=500, detail=str(e))
    
    return {"data": yt_documents}
    
    #return ToolResponse(data=yt_documents)

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

@router.post("/test-quizzify")
async def test_quizzify(
    chat_request: GenericRequest = Depends(validate_multipart_form_data),
    request_files: list[UploadFile] = File(...),
    _ = Depends(key_check)
):
    from features.quizzify.core import executor
    
    if chat_request.tool is None:
        raise HTTPException(status_code=400, detail="Tool not provided")
    
    form_inputs = chat_request.tool.inputs
    
    # Extract topic from form inputs
    topic = next((input for input in form_inputs if input.name == "topic"), None).value
    # Extract number of questions from form inputs
    num_questions = next((input for input in form_inputs if input.name == "num_questions"), None).value
    
    if topic is None:
        raise HTTPException(status_code=400, detail="Topic not provided")
    if num_questions is None:
        raise HTTPException(status_code=400, detail="Number of questions not provided")
    if request_files is None:
        raise HTTPException(status_code=400, detail="File extraction found no files")
    
    return {
        "topic": topic,
        "num_questions": num_questions,
        "request_files": request_files
    }
    
    #return executor(request_files, topic, num_questions)
