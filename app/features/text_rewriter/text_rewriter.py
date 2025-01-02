import sys
import os

# Dynamically add the project root to the PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from fastapi import FastAPI, HTTPException
from app.api.router import router  # Import the router
from app.features.text_rewriter.tools import (
    load_metadata,
    create_input_schema,
    create_output_schema,
    rewrite_tool_handler
)
import uvicorn

# Load metadata.json
metadata = load_metadata()

# Dynamically create Pydantic models
InputModel = create_input_schema(metadata)
OutputModel = create_output_schema(metadata)

# Initialize FastAPI app
app = FastAPI(
    title="Text Rewriter API",
    description="FastAPI application for text rewriting.",
    version="2.0.0"
)

@app.post("/rewrite-text", response_model=OutputModel)
async def rewrite_text(data: InputModel):
    """
    FastAPI endpoint for rewriting text based on metadata.json.
    """
    try:
        # Convert Pydantic model to dict and validate inputs
        inputs = data.dict()
        result = rewrite_tool_handler(inputs)
        return result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Include the router
app.include_router(router)

# Run the app
if __name__ == "__main__":
    uvicorn.run("app.features.text_rewriter.text_rewriter:app", host="0.0.0.0", port=8000, reload=True)