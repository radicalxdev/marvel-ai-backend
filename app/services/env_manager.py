import os
from app.services.logger import setup_logger
from dotenv import load_dotenv, find_dotenv
from google.cloud import secretmanager
import google.auth
import google_crc32c

logger = setup_logger(__name__)

def get_env_variable(var_name):
    """
    Retrieve an environment variable, first from the .env file, 
    and if not found, from Google Cloud Secrets Manager.
    
    :param var_name: The name of the environment variable to retrieve.
    :return: The value of the environment variable.
    """
    # Load environment variables from .env file, if it exists
    load_dotenv(find_dotenv())

    # First, try to retrieve the variable from the .env file
    value = os.getenv(var_name)
    if value is not None:
        logger.debug(f"Successfully retrieved the environment variable '{var_name}' from .env file")
        return value
    
    # If not found, fallback to Google Cloud Secrets Manager
    try:
        # Initialize Google Cloud Secret Manager client
        client = secretmanager.SecretManagerServiceClient()

        # Build the secret name
        secret_name = f"secrets/{var_name}/versions/latest"

        # Access the secret
        response = client.access_secret_version(name=secret_name)

        # Verify payload checksum.
        crc32c = google_crc32c.Checksum()
        crc32c.update(response.payload.data)
        if response.payload.data_crc32c != int(crc32c.hexdigest(), 16):
            error_message = "Data corruption detected: The checksum of the retrieved secret does not match."
            logger.error(error_message)
            raise ValueError(error_message)
        
        secret_payload = response.payload.data.decode('UTF-8')
        logger.debug(f"Successfully retrieved the environment variable '{var_name}' from Google Secrets")
        return secret_payload

    except google.api_core.exceptions.NotFound as e:
        error_message = f"Secret '{var_name}' not found in Google Cloud Secrets Manager: {e}"
        logger.error(error_message)
        raise ValueError(error_message)

    except google.auth.exceptions.DefaultCredentialsError as e:
        error_message = "Google Cloud credentials are not configured properly."
        logger.error(error_message)
        raise RuntimeError(error_message)

    except Exception as e:
        error_message = f"An unexpected error occurred while retrieving '{var_name}' from Google Cloud Secrets Manager: {str(e)}"
        logger.error(error_message)
        raise RuntimeError(error_message)
