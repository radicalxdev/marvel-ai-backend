import os
import pytest
from unittest import mock
from app.services.env_manager import get_env_variable  # Replace 'your_module' with the actual module name where get_env_variable is defined.

def test_get_env_variable_from_dotenv():
    with mock.patch('os.getenv') as mock_getenv:
        mock_getenv.return_value = 'dotenv_value'
        
        result = get_env_variable('MY_VAR')
        assert result == 'dotenv_value'
        mock_getenv.assert_called_once_with('MY_VAR')

@mock.patch('app.services.env_manager.secretmanager.SecretManagerServiceClient')
@mock.patch('os.getenv')
@mock.patch('google_crc32c.Checksum')
def test_get_env_variable_from_gcp(mock_crc32c, mock_getenv, mock_secret_client):
    # Mock dotenv to return None
    mock_getenv.return_value = None

    # Mock Secret Manager client and its response
    mock_secret_client_instance = mock_secret_client.return_value
    mock_secret_version = mock_secret_client_instance.access_secret_version.return_value
    mock_secret_version.payload.data = b"MY_VAR=secret_value"
    mock_secret_version.payload.data_crc32c = 123456789

    # Mock CRC32C checksum verification
    mock_crc32c_instance = mock_crc32c.return_value
    mock_crc32c_instance.update.return_value = None
    mock_crc32c_instance.hexdigest.return_value = '075bcd15'  # corresponds to 123456789 in hex

    result = get_env_variable('MY_VAR')
    assert result == 'secret_value'
    
    mock_getenv.assert_called_once_with('MY_VAR')
    mock_secret_client_instance.access_secret_version.assert_called_once()
    mock_crc32c_instance.update.assert_called_once_with(b"MY_VAR=secret_value")

def test_get_env_variable_raises_exception_on_gcp_error():
    with mock.patch('os.getenv', return_value=None):
        with mock.patch('app.services.env_manager.secretmanager.SecretManagerServiceClient') as mock_secret_client:
            mock_secret_client.return_value.access_secret_version.side_effect = Exception("GCP error")
            
            with pytest.raises(RuntimeError, match="Error retrieving MY_VAR from Google Cloud Secrets Manager: GCP error"):
                get_env_variable('MY_VAR')

def test_get_env_variable_raises_exception_on_credentials_error():
    with mock.patch('os.getenv', return_value=None):
        with mock.patch('app.services.env_manager.secretmanager.SecretManagerServiceClient') as mock_secret_client:
            from google.auth.exceptions import DefaultCredentialsError
            mock_secret_client.return_value.access_secret_version.side_effect = DefaultCredentialsError()
            
            with pytest.raises(RuntimeError, match="Google Cloud credentials are not configured properly."):
                get_env_variable('MY_VAR')
