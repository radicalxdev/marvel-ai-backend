import unittest
from unittest.mock import patch, MagicMock

# Import the function to be tested
from app.services.env_manager import get_env_variable

class TestGetEnvVariable(unittest.TestCase):

    @patch('app.services.env_manager.os.getenv')
    @patch('app.services.env_manager.load_dotenv')
    def test_env_variable_from_env_file(self, mock_load_dotenv, mock_getenv):
        # Setup the mock to return a value as if it was loaded from .env
        mock_getenv.return_value = 'test_value'

        # Call the function
        result = get_env_variable('TEST_VAR')

        # Assert that the .env file was loaded and the getenv was called
        mock_load_dotenv.assert_called_once()
        mock_getenv.assert_called_once_with('TEST_VAR')

        # Check that the value returned is correct
        self.assertEqual(result, 'test_value')

    @patch('app.services.env_manager.secretmanager.SecretManagerServiceClient')
    @patch('app.services.env_manager.os.getenv')
    @patch('app.services.env_manager.load_dotenv')
    def test_env_variable_from_google_secrets(self, mock_load_dotenv, mock_getenv, mock_secret_manager_client):
        # Setup the mock to return None, as if the variable was not found in .env
        mock_getenv.return_value = None

        # Mock the Google Cloud Secret Manager response
        mock_client_instance = MagicMock()
        mock_secret_manager_client.return_value = mock_client_instance
        
        # Mock the secret payload
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

            # Assert that SecretManager was called correctly
            mock_secret_manager_client.assert_called_once()
            mock_client_instance.access_secret_version.assert_called_once_with(name='secrets/TEST_VAR/versions/latest')

            # Check that the value returned is correct
            self.assertEqual(result, 'secret_value')  # Removed .decode('UTF-8')


if __name__ == '__main__':
    unittest.main()
