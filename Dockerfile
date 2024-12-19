# backend/Dockerfile
FROM python:3.10.12

WORKDIR /code

# Install FFmpeg
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir -r /code/requirements.txt

COPY ./app /code/app

# Set environment variable for Python path
ENV PYTHONPATH=/code/app

# Set CMD for running the application
CMD ["fastapi", "dev", "app/main.py", "--host=0.0.0.0", "--port=8000"]