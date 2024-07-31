from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.api.router import router
from app.services.logger import setup_logger
from app.api.error_utilities import ErrorResponse
from dotenv import load_dotenv, find_dotenv
from fastapi import FastAPI, Request, HTTPException
from app.features.syllabus_generator.core import executor
from app.services.tool_registry import ToolInput
from fastapi.encoders import jsonable_encoder

from fastapi import Depends, HTTPException
from fastapi.responses import JSONResponse
from typing import Union,List,Any,Dict
from app.services.schemas import ToolRequest, ToolResponse
from app.utils.auth import key_check
from app.api.error_utilities import InputValidationError
import os

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "local-auth.json"

load_dotenv(find_dotenv())

logger = setup_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Initializing Application Startup")
    try:
        # Perform initialization tasks here
        pass
    except Exception as e:
        logger.error(f"Error during startup: {e}")
        raise
    logger.info(f"Successfully Completed Application Startup")
    
    yield
    logger.info("Application shutdown")

app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error['loc'])
        message = error['msg']
        error_detail = f"Error in field '{field}': {message}"
        errors.append(error_detail)
        logger.error(error_detail)  # Log the error details

    error_response = ErrorResponse(status=422, message=errors)
    return JSONResponse(
        status_code=422,
        content=error_response.dict()
    )

app.include_router(router)

# @app.post("/get_syllabus")
# async def get_syllabus(grade: str, subject: str, Syllabus_type: str):
#     try:
#         if not grade or not subject:
#             raise HTTPException(status_code=400, detail="'grade','subject' and 'Syllabus_type' are required")
        
#         logger.info(f"Received request for grade={grade}, subject={subject}, Syllabus_type={Syllabus_type}")
        
#         # (tool_id=9517, inputs=[])
#         # Assuming executor returns a dictionary or a JSON-serializable object
#         result = executor(grade, subject, Syllabus_type)
        
#         if not isinstance(result, dict):
#             raise ValueError("Executor did not return a dictionary")
        
#         logger.info("Response generated successfully")
#         return JSONResponse(content=result)
#     except ValueError as e:
#         logger.error(f"Error generating syllabus: {e}")
#         raise HTTPException(status_code=500, detail=f"Error generating syllabus: {e}")
#     except Exception as e:
#         logger.error(f"Unexpected error: {e}")
#         raise HTTPException(status_code=500, detail="Internal Server Error")
    
@app.post("/get_syllabus") #response_model=Union[ToolResponse, ErrorResponse])
async def submit_tool(tool_id: int, inputs: List[Dict[str, Any]]):
    try:
        # Call the executor function
        result = executor(tool_id=tool_id, inputs=inputs)
        
        # Return the result wrapped in ToolResponse
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
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

