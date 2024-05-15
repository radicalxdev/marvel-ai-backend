from google.cloud import storage, secretmanager
from google.cloud import logging as cloud_logging
from fastapi import UploadFile, HTTPException
import json
import os
import logging
from io import BytesIO

logger_configured = False

def upload_to_gcs(file: UploadFile, bucket_name: str, blob_name: str):
    """
    Uploads a file to GCS and returns the public URL
    
    Args:
        file (UploadFile): The file to upload
        bucket_name (str): The bucket to upload to
        blob_name (str): The name of the blob to upload to
    
    Returns:
        str: The public URL of the uploaded file
    """
    client = storage.Client()
    bucket = client.get_bucket(bucket_name)
    blob = bucket.blob(blob_name)
    
    blob.upload_from_file(file.file.read(), content_type=file.content_type)
    file.file.close()
    
    return blob.public_url

def download_from_gcs(bucket_name: str, blob_name: str) -> BytesIO:
    """
    Downloads a file from GCS and returns it as a BytesIO object.
    
    This allows the file to be read into memory, suitable for files like PDFs.
    
    Args:
        bucket_name (str): The name of the bucket to download from.
        blob_name (str): The full path of the blob within the bucket to download.
    
    Returns:
        BytesIO: An in-memory file object that can be read or written to.
    """
    client = storage.Client()
    bucket = client.get_bucket(bucket_name)
    blob = bucket.blob(blob_name)
    
    # Create an in-memory bytes buffer
    bytes_buffer = BytesIO()
    
    # Download the blob to the in-memory bytes buffer
    blob.download_to_file(bytes_buffer)
    
    # Reset buffer position to the beginning after writing
    bytes_buffer.seek(0)
    
    return bytes_buffer

def delete_from_gcs(bucket_name: str, blob_name: str):
    """
    Deletes a file from GCS
    
    Args:
        bucket_name (str): The bucket to delete from
        blob_name (str): The name of the blob to delete
    """
    client = storage.Client()
    bucket = client.get_bucket(bucket_name)
    blob = bucket.blob(blob_name)
    
    blob.delete()

def setup_logger(name=__name__):
    """
    Sets up a logger based on the environment.

    If the environment variable ENV_TYPE is set to 'sandbox' or 'production', it configures
    Google Cloud Logging. Otherwise, it uses the standard logging.

    Parameters:
    name (str): The name of the logger.

    Returns:
    logging.Logger: Configured logger.
    """
    env_type = os.environ.get('ENV_TYPE', 'undefined')
    project = os.environ.get('PROJECT_ID', 'undefined')
    global logger_configured

    print(f"Attempting to establish logger for {env_type} environment in project: {project}")

    logger = logging.getLogger(name)
    
    # Check if the logger already has handlers configured.
    # This prevents adding multiple handlers to the same logger if setup_logger is called multiple times.
    if not logger_configured:
        if env_type in ['sandbox', 'production']:
            try:
                logging_client = cloud_logging.Client(project=project)
                cloud_logging_handler = logging_client.get_default_handler()
                formatter = logging.Formatter(f'%(asctime)s - {env_type} - %(name)s - %(levelname)s - %(message)s')
                cloud_logging_handler.setFormatter(formatter)
                logger.addHandler(cloud_logging_handler)
                logger.setLevel(logging.INFO)
                print(f"ESTABLISHED CLOUD LOGGER: {env_type} for project: {project}")
                logger_configured = True
            except Exception as e:
                print(f"Failed to configure Google Cloud Logging: {str(e)}")
                # Fall back to standard logging if GCL configuration fails
                logger.addHandler(logging.StreamHandler())
        else:
            # For 'dev' or undefined environments, configure standard logging
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
            print("ESTABLISHED STANDARD LOGGER for non-production/local environments")
    else:
        print(f"Logger for {name} already configured.")
        return logging.getLogger(name)

    return logger

def access_secret_file(secret_id, version_id="latest"):
    """
    Access a secret file in Google Cloud Secret Manager and parse it.
    """
    project_id = os.environ.get('PROJECT_ID')
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
    response = client.access_secret_version(name=name)
    return response.payload.data.decode("UTF-8")

def read_blob_to_string(bucket_name, file_path):
    storage_client = storage.Client()

    try: 
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(file_path)
        content = blob.download_as_bytes()
        
        return content.decode("utf-8")  # Decode the byte string
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Request not found: {e}")
  
def read_json_blob(bucket_name=None, blob_name=None, credentials_path=None):
    """
    Reads the content of a JSON blob from Google Cloud Storage and returns it as a Python dictionary.

    Parameters:
    bucket_name (str, optional): The name of the GCS bucket. Defaults to the BUCKET_NAME environment variable if not provided.
    blob_name (str, optional): The name of the blob (file) to read. Defaults to the BLOB_NAME environment variable if not provided.
    credentials_path (str, optional): The path to the service account JSON file for GCS authentication. If not provided, defaults to the credentials configured in the environment.

    Returns:
    dict: The content of the JSON file.

    Raises:
    HTTPException: If the blob is not found or if there's an error in reading the blob.
    """
    # Use environment variables if parameters are not provided
    bucket_name = bucket_name or os.environ.get('BUCKET_NAME')
    blob_name = blob_name or os.environ.get('BLOB_NAME')

    if not bucket_name or not blob_name:
        raise ValueError("Bucket name and Blob name must be provided")

    try:
        # If you are not using the environment variable for credentials
        if credentials_path:
            storage_client = storage.Client.from_service_account_json(credentials_path)
        else:
            storage_client = storage.Client()

        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        content = blob.download_as_bytes()

        # Parse the JSON content
        return json.loads(content.decode("utf-8"))
    
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="JSON file not found in the bucket.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while reading the blob: {str(e)}")
