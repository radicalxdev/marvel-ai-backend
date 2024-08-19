# Use an official Python runtime as a parent image
FROM python:3.10.12

# Set the working directory in the container
WORKDIR /code

# Copy the requirements file into the container at /code/
COPY requirements.txt /code/requirements.txt

# Install any dependencies
RUN pip install --no-cache-dir -r /code/requirements.txt

# Copy the rest of the application code to /code/
COPY ./app /code/app

# Set environment variables
ENV PYTHONPATH=/code/app

# Copy the service account key file
COPY local-auth.json /code/local-auth.json

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Define the command to run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
