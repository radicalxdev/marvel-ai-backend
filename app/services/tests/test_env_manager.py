import pytest
from unittest.mock import patch, MagicMock
from dotenv import find_dotenv

# Import the function to be tested
from app.services.env_manager import get_env_variable

@patch('app.services.env_manager.os.getenv')
@patch('app.services.env_manager.load_dotenv')
def test_env_variable_from_env_file(mock_load_dotenv, mock_getenv):
    # Setup the mock to return a value as if it was loaded from .env
    mock_getenv.return_value = 'test_value'

    # Call the function
    result = get_env_variable('TEST_VAR')

    # Assert that the .env file was loaded and the getenv was called
    mock_load_dotenv.assert_called_once_with(find_dotenv())
    mock_getenv.assert_called_once_with('TEST_VAR')

    # Check that the value returned is correct
    assert result == 'test_value'

@patch('app.services.env_manager.secretmanager.SecretManagerServiceClient')
@patch('app.services.env_manager.os.getenv')
@patch('app.services.env_manager.load_dotenv')
@patch('app.services.env_manager.default')
def test_env_variable_from_google_secrets(mock_default, mock_load_dotenv, mock_getenv, mock_secret_manager_client):
    # Setup the mock to return None, as if the variable was not found in .env
    mock_getenv.return_value = None

    # Mock the default credentials and project ID
    mock_default.return_value = (MagicMock(), 'mock_project_id')

    # Mock the Google Cloud Secret Manager client and response
    mock_client_instance = MagicMock()
    mock_secret_manager_client.return_value = mock_client_instance

    mock_response = MagicMock()
    mock_response.payload.data = b'secret_value'
    mock_response.payload.data_crc32c = 123456789  # some checksum value
    mock_client_instance.access_secret_version.return_value = mock_response

    # Patch the CRC32C checksum verification
    with patch('app.services.env_manager.google_crc32c.Checksum') as mock_crc32c:
        mock_crc32c_instance = MagicMock()
        mock_crc32c.return_value = mock_crc32c_instance
        mock_crc32c_instance.update.return_value = None
        mock_crc32c_instance.hexdigest.return_value = hex(123456789)[2:]

        # Call the function
        result = get_env_variable('TEST_VAR')

        # Assert that the .env file was loaded and the getenv was called
        mock_load_dotenv.assert_called_once_with(find_dotenv())
        mock_getenv.assert_called_once_with('TEST_VAR')

        # Assert that SecretManager was called correctly
        mock_secret_manager_client.assert_called_once()
        mock_client_instance.access_secret_version.assert_called_once_with(
            name='projects/mock_project_id/secrets/TEST_VAR/versions/latest'
        )

        # Check that the value returned is correct
        assert result == 'secret_value'
