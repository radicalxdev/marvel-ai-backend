from fastapi import HTTPException, Header

# Function to ensure incoming request is from controller with key
def key_check(api_key: str = Header(None)):
  set_key = "dev"
  
  if api_key is None or api_key != set_key:
    raise HTTPException(status_code=401, detail="Invalid API Request Key")