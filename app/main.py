from fastapi import FastAPI, Request, Depends
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.api.router import router
from app.services.logger import setup_logger
from app.api.error_utilities import ErrorResponse
# FastAPI core imports
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse,StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError

import os
from dotenv import load_dotenv, find_dotenv

from app.features.ai_resistant_assignment_generator.core import executor
from app.features.rubric_generator.core import executor2
from app.services.schemas import ToolResponse,InputData, AIRAGRequest, RUBRICRequest

load_dotenv(find_dotenv())

logger = setup_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Initializing Application Startup")
    logger.info(f"Successfully Completed Application Startup")
    
    yield
    logger.info("Application shutdown")

app = FastAPI(lifespan = lifespan)
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

@app.post("/ai_reisistant_assignment_generator")
async def ai_resistant(inputs:AIRAGRequest,Type: str = ''):
    try:
        # Call the executor function
        if not Type:
            result = await executor(inputs=inputs)
            return ToolResponse(data=result)
        else :
            result = await executor(inputs=inputs,Type=Type)
            return StreamingResponse(result['file'], media_type=result['type'])

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.post("/rubric_generator")
async def rubric_generator(inputs:RUBRICRequest,Type: str = ''):
    try:
        # Call the executor function
        if not Type:
            result = await executor2(inputs=inputs)
            return ToolResponse(data=result)
        else :
            result = await executor(inputs=inputs,Type=Type)
            return StreamingResponse(result['file'], media_type=result['type'])

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
app.include_router(router)