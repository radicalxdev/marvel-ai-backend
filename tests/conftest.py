import pytest
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

@pytest.fixture(scope='session', autouse=True)
def load_env():
    # Ensure the environment variables are set
    google_api_key = os.getenv('9fc1ba45f9da13d719a20cd660baff7882368bf1')
    google_application_credentials = os.getenv('C:/Users/steve/marvel-ai-backend/marvel-ai-backend/custom-dominion-446220-m9-9fc1ba45f9da.json')

    if google_api_key is None:
        raise ValueError("GOOGLE_API_KEY environment variable is not set")
    if google_application_credentials is None:
        raise ValueError("GOOGLE_APPLICATION_CREDENTIALS environment variable is not set")