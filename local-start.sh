echo "Starting local server\n"

export LANGCHAIN_TRACING_V2=true
export LANGCHAIN_ENDPOINT="https://api.smith.langchain.com"
export LANGCHAIN_API_KEY=$LANGSMITH_API_KEY
export LANGCHAIN_PROJECT=$LANGSMITH_PROJECT

# Authenticate GCP project with service account credentials
export GOOGLE_APPLICATION_CREDENTIALS=$(pwd)/app/local-auth.json

# Import the Python module to fetch environment variables
PYTHON_COMMAND="from app.services.env_manager import get_env_variable;"

# Fetch and set the environment variables
export GOOGLE_API_KEY=$(python3 -c "$PYTHON_COMMAND print(get_env_variable('GOOGLE_API_KEY'))")
export ENV_TYPE=$(python3 -c "$PYTHON_COMMAND print(get_env_variable('ENV_TYPE'))")
export PROJECT_ID=$(python3 -c "$PYTHON_COMMAND print(get_env_variable('GCP_PROJECT_ID'))")

export PYTHONPATH=$(pwd)/app

echo "Loaded environment variables:"
echo "LANGCHAIN_TRACING_V2: $LANGCHAIN_TRACING_V2"
echo "LANGCHAIN_ENDPOINT: $LANGCHAIN_ENDPOINT"
echo "LANGCHAIN_API_KEY: $LANGCHAIN_API_KEY"
echo "LANGCHAIN_PROJECT: $LANGCHAIN_PROJECT"
echo "ENV_TYPE: $ENV_TYPE"
echo "PROJECT_ID: $PROJECT_ID"
echo "GOOGLE_API_KEY: $GOOGLE_API_KEY"

fastapi dev app/main.py
