from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, UploadFile, File, Form

import json

from app.services.logger import setup_logger
from app.features.connect_with_them.tools import Agent_executor
from app.features.connect_with_them.prompt.Prompts import Prompt_query

logger = setup_logger()

app = FastAPI()

class ExecutorRequest(BaseModel):
    grade: str
    subject: str
    description: str

@app.post("/execute/")
async def execute(request: ExecutorRequest, file: UploadFile = File(None)):
    grade = request.grade
    subject = request.subject
    description = request.description
    if not (grade and subject):
        raise HTTPException(status_code=400, detail="Grade and subject are required")
    try:
        user_input = Prompt_query(grade, subject, description)
        result = Agent_executor.invoke({'input': user_input})
        try :
            formated_output = result['output'].replace('\n','')
            output = json.loads(formated_output)
        except Exception as e:
            output = result['output']
        return output

    except Exception as e:
        error_message = f"Error in executor: {e}"
        logger.error(error_message)
        raise HTTPException(status_code=500, detail=error_message)
