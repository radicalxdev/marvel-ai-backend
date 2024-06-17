export GOOGLE_APPLICATION_CREDENTIALS=$(pwd)/app/local-auth.json
export ENV_TYPE=dev
export PROJECT_ID=kai-ai-f63c8
export PYTHONPATH=$(pwd)/app

fastapi dev app/main.py