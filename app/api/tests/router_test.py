from fastapi.testclient import TestClient
from ...main import app  # Make sure this import points to your FastAPI app instance
from app.services.gcp import access_secret_file
import pytest
import os
import json
from base64 import b64encode

# Function to encode a file to base64
def encode_file_to_base64(file_path):
    with open(file_path, "rb") as file:
        return b64encode(file.read()).decode('utf-8')

@pytest.fixture(scope='session', autouse=True)
def set_env_vars():
    # Backup old values and set new ones
    old_creds = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    old_env_type = os.getenv('ENV_TYPE')
    old_project_id = os.getenv('PROJECT_ID')
    # Set new values
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'app/local-auth.json'
    os.environ['ENV_TYPE'] = 'sandbox'
    # Ensure these changes are only present during the tests
    yield
    # Restore old values after tests
    if old_creds:
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = old_creds
    if old_env_type:
        os.environ['ENV_TYPE'] = old_env_type
    if old_project_id:
        os.environ['PROJECT_ID'] = old_project_id

@pytest.fixture
def client():
    return TestClient(app)

def test_quizzify_simple(client):
    data = {
        "user": {
            "id": "string",
            "fullName": "string",
            "email": "string"
        },
        "type": "tool",
        "tool": {
            "id": 0,
            "inputs": [
                {"name": "topic", "value": "Mathematics"},
                {"name": "num_questions", "value": 2},
                {"name": "upload_files", "value": ""}
            ]
        }
    }

    headers = { "Content-Type": "application/json", "api-key": "AIzaSyBT0cxIrvcSUL8Ylfmrt8gra9BYb_K20kE" }

    response = client.post("/test-quizzify", json=data, headers=headers)
    
    if response.status_code != 200:
        print("Response status:", response.status_code)
        print("Response body:", response.json())

    assert response.status_code == 200

def test_quzzify_file(client):
    # Prepare the data as JSON including the base64 encoded file
    encoded_pdf = encode_file_to_base64('app/api/tests/test.pdf')
    
    data = {
        "user": {
            "id": "string",
            "fullName": "string",
            "email": "string"
        },
        "type": "tool",
        "tool": {
            "id": 0,
            "inputs": [
                {"name": "topic", "value": "Mathematics"},
                {"name": "num_questions", "value": 2},
                {"name": "upload_files", "value": f"data:application/pdf;base64,{encoded_pdf}"}
            ]
        }
    }

    headers = { "Content-Type": "application/json", "api-key": {access_secret_file("backend-access")} }

    response = client.post("/test-quizzify", json=data, headers=headers)
    
    if response.status_code != 200:
        print("Response status:", response.status_code)
        print("Response body:", response.json())

    assert response.status_code == 200
    
    return response.json()

