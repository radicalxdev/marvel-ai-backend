from fastapi.testclient import TestClient
from ...main import app  
from services.gcp import access_secret_file
import pytest
import os

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

