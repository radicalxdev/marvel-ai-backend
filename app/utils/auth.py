from fastapi import HTTPException, Header
#from google.cloud import secretmanager
#from google.oauth2 import service_account
import os

# def access_secret_file(secret_id, version_id="latest"):
#     """
#     Access a secret file in Google Cloud Secret Manager and parse it.
#     """
#     project_id = os.environ.get('PROJECT_ID')
#     json_dir = os.path.dirname(os.path.abspath(__file__))
#     credentials = service_account.Credentials.from_service_account_file(os.path.join(json_dir, "keyfile.json"))
#     client = secretmanager.SecretManagerServiceClient(credentials=credentials)
#     name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
#     response = client.access_secret_version(name=name)
#     return response.payload.data.decode("UTF-8")

# Function to ensure incoming request is from controller with key
def key_check(api_key: str = Header(None)):

  if os.environ['ENV_TYPE'] == "production":
    set_key = os.environ['PRODUCTION_API_KEY']
  else:
    set_key = "dev"
  
  if api_key is None or api_key != set_key:
    raise HTTPException(status_code=401, detail="Invalid API Request Key")