from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import vertexai
from vertexai.generative_models import GenerativeModel

# Load environment variables from the .env file
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), 'text_rewriter.env'))

# Load API keys and credentials from environment variables
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
PROJECT_ID = os.getenv("PROJECT_ID")
GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

if not GOOGLE_API_KEY or not PROJECT_ID or not GOOGLE_APPLICATION_CREDENTIALS:
    raise Exception("API keys or project ID or credentials are missing. Please check your .env file.")

# Set the environment variable for Google Cloud authentication
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GOOGLE_APPLICATION_CREDENTIALS

# Initialize Vertex AI client
vertexai.init(project=PROJECT_ID, location="us-central1")

# Define router
router = APIRouter()

# Input schema
class RewriteRequest(BaseModel):
    text: str
    instructions: str

# Output schema
class RewriteResponse(BaseModel):
    rewritten_text: str

# Endpoint to handle text rewriting
@router.post("/rewrite_text", response_model=RewriteResponse)
async def rewrite_text(request: RewriteRequest):
    try:
        # Get input text and instructions
        input_text = request.text
        instructions = request.instructions
        
        if not input_text or not instructions:
            raise HTTPException(status_code=400, detail="Text input and instructions are required")
        
        # Construct the prompt
        prompt = f"Task: {instructions}\n\nText: {input_text}"

        # Use Gemini 1.5 to process the input text with the model
        model = GenerativeModel("gemini-1.5-flash-002")

        # Generate content using the Gemini model
        response = model.generate_content(prompt)

        # Return the rewritten text
        rewritten_text = response.text

        return RewriteResponse(rewritten_text=rewritten_text)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing text with Gemini: {str(e)}")