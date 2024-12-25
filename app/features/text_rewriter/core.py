import os
from google.cloud import aiplatform
from dotenv import load_dotenv

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
aiplatform.init(project=PROJECT_ID, location="us-central1")

def process_text_with_gemini(text: str, instructions: str) -> dict:
    try:
        # Create the prompt combining the instructions and input text
        prompt = f"Task: {instructions}\n\nText: {text}"

        # Instantiate the PredictionServiceClient and the model you want to use
        prediction_client = aiplatform.gapic.PredictionServiceClient()

        # Define the model's name (Gemini 1.5)
        model_name = f"projects/{PROJECT_ID}/locations/us-central1/models/gemini-1.5-flash-002"

        # Prepare the request with the prompt
        instance = {"content": prompt}
        instances = [instance]

        # Request prediction using the model
        response = prediction_client.predict(instances=instances, endpoint=model_name)
        
        # Get the result from the response
        rewritten_text = response.predictions[0].get('content', 'No output generated')

        return {"rewritten_text": rewritten_text}

    except Exception as e:
        print(f"Error: {str(e)}")  # This will give you a direct printout of the error in your terminal
        raise Exception(f"Error processing text with Gemini: {str(e)}")