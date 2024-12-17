# backend/Dockerfile
FROM python:3.10.12

WORKDIR /code

# Install FFmpeg
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir -r /code/requirements.txt

COPY ./app /code/app

# Argument for the credentials JSON
ARG CREDENTIALS_JSON

# Ensure the directory exists and create the keyfile.json
RUN mkdir -p /code/app/utils && \
    echo "$CREDENTIALS_JSON" > /code/app/utils/keyfile.json

# Set environment variable for Python path
ENV PYTHONPATH=/code/app

# Set CMD for running the application
CMD ["fastapi", "dev", "app/main.py", "--host=0.0.0.0", "--port=8000"]