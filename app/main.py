from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.api.router import router
from app.services.logger import setup_logger
from app.api.error_utilities import ErrorResponse
from dotenv import load_dotenv, find_dotenv
from fastapi import FastAPI, Request ,HTTPException
from app.features.syllabus_generator.core import executor

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

app.include_router(router)



### THE FOLLOWING ARE PARTS THAT WERE ADDED ###

@app.post("/get_syllabus")
async def get_syllabus(grade: str, subject: str, Syllabus_type:str):
    try:
        if not grade or not subject:
            raise HTTPException(status_code=400, detail="Both 'grade' and 'subject' are required")
        
        logger.info(f"Received request for grade={grade}, subject={subject}, Syllabus_type={Syllabus_type}")
        result = executor(grade, subject, Syllabus_type)
        logger.info("Response generated successfully")
        return result
    except ValueError as e:
        logger.error(f"Error generating syllabus: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating syllabus: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
# @app.post("/get_syllabus")
# def get_syllabus(grade: str, subject: str) :
#     try:
#         syllabus = executor(grade, subject)
#         return syllabus
#     except Exception as e:
#         logger.error(f"Error generating syllabus: {str(e)}")
#         raise HTTPException(status_code=500, detail="An error occurred while generating the syllabus")
