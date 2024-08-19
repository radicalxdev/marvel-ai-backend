import logging
import os
from dotenv import load_dotenv,find_dotenv

# Load environment variables from .env file
load_dotenv(find_dotenv())

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

    # Obtain a reference to the logger
    logger = logging.getLogger(name)

    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
        logger.propagate = True

    return logger