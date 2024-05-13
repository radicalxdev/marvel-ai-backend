from fastapi.testclient import TestClient
from main import app  
from services.gcp import access_secret_file
from services.tool_registry import validate_inputs
from io import BytesIO
import pytest
import os
import json
import tempfile

#export PYTHONPATH=/path/to/your/project:$PYTHONPATH
#pytest -v

@pytest.fixture(scope='session', autouse=True)
def set_env_vars():
    # Backup old values and set new ones
    old_creds = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    old_env_type = os.getenv('ENV_TYPE')
    old_project_id = os.getenv('PROJECT_ID')
    # Set new values
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'local-auth.json'
    os.environ['ENV_TYPE'] = 'dev'
    os.environ['PROJECT_ID'] = "kai-ai-f63c8"
    os.environ['api-key'] = access_secret_file('backend-access')
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
    with TestClient(app) as client:
        yield client

def create_mock_pdf() -> BytesIO:
    """
    Creates a mock PDF file in memory.
    """
    # Create a bytes buffer (in-memory bytes object)
    pdf = BytesIO()
    
    # Writing mock content. This is not a valid PDF content but is fine for simulating a file upload.
    # For a more realistic simulation, you could use actual PDF header bytes and structures.
    pdf.write(b'%PDF-1.4\n%Mock PDF file for testing\n')
    
    # Important: seek to the start of the BytesIO object so it can be read from the beginning
    pdf.seek(0)
    return pdf


# Test cases
def atest_quizzify_tool_submission(client: TestClient):
    data_dict = {
        "user": {
            "id": "string",
            "fullName": "string",
            "email": "string"
        },
        "type": "tool",
        "tool_data": {
            "tool_id": 0,
            "inputs": [
            {
                "name": "topic",
                "value": "Math"
            },
            {
                "name": "num_questions",
                "value": 5
            }
            ]
        }
    }
    
    response = client.post(
            "/submit-tool",
            json=data_dict
        )

    assert response.status_code == 200


def test_quizzify_tool_submission_with_files(client: TestClient):
    data_dict = {
        "user": {
            "id": "string",
            "fullName": "string",
            "email": "string"
        },
        "type": "tool",
        "tool_data": {
            "tool_id": 1,
            "inputs": [
                {
                    "name": "youtube_url",
                    "value": "https://www.youtube.com/watch?v=J4ZzZ8JZ9cA"
                }
            ]
        }
    }
    
    json_data = json.dumps(data_dict)
    print(json_data)
    
    pdf_file2 = create_mock_pdf()

    # Create a temporary file to write the mock PDF
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(pdf_file2.getvalue())
        temp_pdf_path = tmp.name

    files = [
        ("files", ("file1.pdf", open("api/tests/test.pdf", "rb"), "application/pdf")),
        ("files", ("file2.pdf", open(temp_pdf_path, "rb"), "application/pdf"))
    ]
    
    data = {"data": json_data}
    
    headers = {"api-key": access_secret_file('backend-access')}
    
    response = client.post("/submit-tool", headers=headers, data=data, files=files)
    
    print(response.text)

    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    assert response.json()["files"] == 2


def test_validate_inputs_all_valid():
    # This mimics the structure that would be created in the endpoint
    # from request_data.inputs where each input is an instance with a name and value attribute
    request_inputs = [
        {"name": "topic", "value": "Quantum Mechanics"}, 
        {"name": "num_questions", "value": 5}
    ]
    
    firestore_data = [
        {"label": "Topic", "type": "text", "name": "topic"},
        {"label": "Number of Questions", "type": "number", "name": "num_questions"}
    ]
    
    # Convert request_inputs to the dictionary format expected by validate_inputs
    request_inputs_dict = {input_item["name"]: input_item["value"] for input_item in request_inputs}
    
    assert validate_inputs(request_inputs_dict, firestore_data) == True

def test_validate_inputs_missing_input():
    request_inputs = [
        {"name": "topic", "value": "Quantum Mechanics"}
    ]
    firestore_data = [
        {"label": "Topic", "type": "text", "name": "topic"},
        {"label": "Number of Questions", "type": "number", "name": "num_questions"}
    ]
    request_inputs_dict = {input_item["name"]: input_item["value"] for input_item in request_inputs}
    assert validate_inputs(request_inputs_dict, firestore_data) == False

def test_validate_inputs_invalid_type():
    request_inputs = [
        {"name": "topic", "value": "Quantum Mechanics"}, 
        {"name": "num_questions", "value": "five"}
    ]
    firestore_data = [
        {"label": "Topic", "type": "text", "name": "topic"},
        {"label": "Number of Questions", "type": "number", "name": "num_questions"}
    ]
    request_inputs_dict = {input_item["name"]: input_item["value"] for input_item in request_inputs}
    assert validate_inputs(request_inputs_dict, firestore_data) == False

def test_validate_inputs_extra_undefined_input():
    request_inputs = [
        {"name": "topic", "value": "Quantum Mechanics"}, 
        {"name": "num_questions", "value": 5},
        {"name": "extra_input", "value": "Extra Value"}
    ]
    firestore_data = [
        {"label": "Topic", "type": "text", "name": "topic"},
        {"label": "Number of Questions", "type": "number", "name": "num_questions"}
    ]
    request_inputs_dict = {input_item["name"]: input_item["value"] for input_item in request_inputs}
    assert validate_inputs(request_inputs_dict, firestore_data) == True

def test_validate_inputs_input_not_found():
    request_inputs = [
        {"name": "unknown_input", "value": "Some Value"}
    ]
    firestore_data = [
        {"label": "Topic", "type": "text", "name": "topic"},
        {"label": "Number of Questions", "type": "number", "name": "num_questions"}
    ]
    request_inputs_dict = {input_item["name"]: input_item["value"] for input_item in request_inputs}
    assert validate_inputs(request_inputs_dict, firestore_data) == False
