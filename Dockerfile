# backend/Dockerfile
FROM python:3.10.12

WORKDIR /app

COPY app/ /app

RUN pip install --no-cache-dir -r /app/requirements.txt

COPY ./app /app

# Local development key set
# ENV GOOGLE_APPLICATION_CREDENTIALS=/app/local-auth.json 
ENV ENV_TYPE="dev"
ENV PROJECT_ID="kai-ai-f63c8"

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
