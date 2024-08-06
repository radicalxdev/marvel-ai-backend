# Standard library imports
import os

# FastAPI core imports
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse,StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder

# Context management imports
from contextlib import asynccontextmanager

# Application-specific imports
from app.api.router import router
from app.services.logger import setup_logger
from app.api.error_utilities import ErrorResponse, InputValidationError
from app.features.syllabus_generator.core import executor,InputData
from app.services.schemas import ToolResponse

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "local-auth.json"

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
app.include_router(router)

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

@app.post("/get_syllabus")
async def submit_tool(inputs: InputData,tool_id: int=3):
    try:
        # Call the executor function
        result = executor(tool_id=tool_id, inputs=inputs)
        if tool_id == 2 :
            return StreamingResponse(result, media_type="application/pdf")
        if tool_id == 3:
            return StreamingResponse(result, media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
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
