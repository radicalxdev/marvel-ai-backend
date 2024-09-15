# Use the official Python image from the Docker Hub
FROM python:3.10.12

# Set the working directory in the container
WORKDIR /code

# Copy the dependencies file to the working directory
COPY requirements.txt /code/requirements.txt

# Install any dependencies
RUN pip install --no-cache-dir -r /code/requirements.txt

# Copy the application code to the working directory
COPY ./app /code/app

# Set the environment variable for local development (optional)
ENV ENV_TYPE=dev

# Expose the port FastAPI runs on
EXPOSE 8000

# Run the FastAPI application using uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]


# backend/Dockerfile
# FROM python:3.10.12

# WORKDIR /code

# COPY requirements.txt /code/requirements.txt

# RUN pip install --no-cache-dir -r /code/requirements.txt

# COPY ./app /code/app

# # Local development key set
# # ENV TYPES: dev, production
# # When set to dev, API Key on endpoint requests are just 'dev'
# # When set to production, API Key on endpoint requests are the actual API Key

# ENV PYTHONPATH=/code/app

# CMD ["fastapi", "dev", "app/main.py", "--host=0.0.0.0", "--port=8000"]


