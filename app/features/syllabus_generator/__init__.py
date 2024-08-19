from dotenv import load_dotenv, find_dotenv
import os

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "local-auth.json"

load_dotenv(find_dotenv())

credentials =   {
        'client_id' : os.getenv('CLIENT_ID'),
        'client_secret' : os.getenv('CLIENT_SECRET'),
        'username' : os.getenv('NAME'),
        'password' : os.getenv('PASSWORD'),
        'user_agent' : os.getenv('USER_AGENT'),
        'search_engine_id' : os.getenv('SEARCH_ENGINE_ID'),
        'api_key' : os.getenv('API_KEY'),
    }
