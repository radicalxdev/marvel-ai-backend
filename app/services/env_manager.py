import os
from dotenv import load_dotenv, find_dotenv
from google.cloud import secretmanager
import google.auth
import google_crc32c

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
        return value
    
    # If not found, fallback to Google Cloud Secrets Manager
    try:
        # Initialize Google Cloud Secret Manager client
        client = secretmanager.SecretManagerServiceClient()

        # Use the environment variable for project ID or default to the GCP_PROJECT_ID from .env
        project_id = 'kai-ai-432116'

        # Build the secret name
        secret_name = f"projects/{project_id}/secrets/env/versions/latest"

        # Access the secret
        response = client.access_secret_version(name=secret_name)
        
        # Verify payload checksum.
        crc32c = google_crc32c.Checksum()
        crc32c.update(response.payload.data)
        if response.payload.data_crc32c != int(crc32c.hexdigest(), 16):
            print("Data corruption detected.")
            return response
        
        secret_payload = response.payload.data.decode('UTF-8')
        # Parse the payload as if it were a .env file
        env_vars = {}
        for line in secret_payload.splitlines():
            if line.strip() and not line.startswith('#'):
                key, val = line.split('=', 1)
                env_vars[key.strip()] = val.strip()
        
        # Retrieve the desired variable from the parsed payload
        print("successfully retrieve the variable")
        return env_vars.get(var_name)
    
    except google.auth.exceptions.DefaultCredentialsError:
        raise RuntimeError("Google Cloud credentials are not configured properly.")
    except Exception as e:
        raise RuntimeError(f"Error retrieving {var_name} from Google Cloud Secrets Manager: {str(e)}")
    

