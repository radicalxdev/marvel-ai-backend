# backend/Dockerfile
FROM python:3.10.12

WORKDIR /app

COPY app/ /app

RUN pip install --no-cache-dir -r /app/requirements.txt

COPY ./app /app

# Local development key set
ENV GOOGLE_APPLICATION_CREDENTIALS=/app/local-auth.json 
ENV ENV_TYPE="dev"
ENV PROJECT_ID="kai-ai-f63c8"

# Langsmith Monitoring
ENV LANGCHAIN_TRACING_V2=true
ENV LANGCHAIN_ENDPOINT="https://api.smith.langchain.com"
ENV LANGCHAIN_API_KEY="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"
ENV LANGCHAIN_PROJECT="Quizzify"

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
