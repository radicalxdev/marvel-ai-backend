import os
from googleapiclient.discovery import build
from google.cloud import aiplatform
from fastapi import FastAPI, HTTPException, Request
from dotenv import load_dotenv
from core import process_text_with_gemini  # Assuming your Gemini logic is here
from tools import TextRewriterInput, TextRewriterOutput  # Pydantic models for validation
from router import router as text_rewriter_router  # Import the router for routing

# Load environment variables from the .env file
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), 'text_rewriter.env'))

# Load API keys and credentials from environment variables
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
PROJECT_ID = os.getenv("PROJECT_ID")
GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

if not GOOGLE_API_KEY or not PROJECT_ID or not GOOGLE_APPLICATION_CREDENTIALS:
    raise Exception("API keys, project ID, or credentials are missing. Please check your .env file.")

# Set the environment variable for Google Cloud authentication
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GOOGLE_APPLICATION_CREDENTIALS

# Initialize Vertex AI client
aiplatform.init(project=PROJECT_ID, location="us-central1")

# Initialize FastAPI app
app = FastAPI()

# Include the router for any other endpoints you may have
app.include_router(text_rewriter_router)


# Start the FastAPI app if this script is run directly
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)