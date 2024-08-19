# Standard library imports
import os
from typing import Optional

# FastAPI core imports
from fastapi import FastAPI, Request, HTTPException, File, UploadFile, Form
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError

# Context management imports
from contextlib import asynccontextmanager

# Application-specific imports
from app.api.router import router
from app.services.logger import setup_logger
from app.api.error_utilities import ErrorResponse, InputValidationError
from app.features.syllabus_generator.core import executor
from app.services.schemas import ToolResponse, InputData

# Environment setup
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "local-auth.json"

# Logger setup
logger = setup_logger(__name__)

# Context manager for application lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing Application Startup")
    try:
        # Perform initialization tasks here
        pass
    except Exception as e:
        logger.error(f"Error during startup: {e}")
        raise
    logger.info("Successfully Completed Application Startup")

    yield  # This point represents the lifespan of the application

    logger.info("Application shutdown")

# FastAPI application setup
app = FastAPI(lifespan=lifespan)

# Middleware configuration for CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the application router
app.include_router(router)

# Custom exception handler for request validation errors
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

# Endpoint to get syllabus
@app.post("/get_syllabus")
async def get_syllabus(
    grade: str = Form(...),
    subject: str = Form(...),
    syllabus_type: str = Form(...),
    instructions: str = Form(...),
    file: Optional[UploadFile] = File(None),
    type_: str = Form('')  # Renamed 'Type' to 'type_' to avoid conflict with Python's built-in 'type'
):
    try:
        # Prepare input data
        inputs = InputData(
            grade=grade,
            subject=subject,
            Syllabus_type=syllabus_type,
            instructions=instructions
        )

        # Execute the core functionality based on 'type_' parameter
        if not type_:
            result = await executor(inputs=inputs, file=file)
            return ToolResponse(data=result)
        else:
            result = await executor(inputs=inputs, file=file, Type=type_)
            return StreamingResponse(result['file'], media_type=result['type'])

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
