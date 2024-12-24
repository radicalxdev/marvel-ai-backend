from fastapi import HTTPException, Header
import os

# Function to ensure incoming request is from controller with key
def key_check(api_key: str = Header(None)):

  if os.environ['ENV_TYPE'] == "production":
    set_key = os.environ['PRODUCTION_API_KEY']
  else:
    set_key = "dev"
  
  if api_key is None or api_key != set_key:
    raise HTTPException(status_code=401, detail="Invalid API Request Key")