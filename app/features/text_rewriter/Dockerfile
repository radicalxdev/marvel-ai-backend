# Use Python 3.12 slim image
FROM python:3.12-slim

# Set working directory inside the container
WORKDIR /app

# Copy requirements.txt and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && rm -rf /root/.cache
    
# Copy the .json service account file into the container
COPY gen-lang-client-0717318025-ef6f992883f8.json /app/gen-lang-client-0717318025-ef6f992883f8.json

# Set the environment variable for Google Cloud authentication
ENV GOOGLE_APPLICATION_CREDENTIALS=/app/gen-lang-client-0717318025-ef6f992883f8.json

# Copy the application source code into the container
COPY . .

# Create a virtual environment (optional but recommended)
RUN python3 -m venv /venv

# Use the virtual environment and install dependencies there
RUN /venv/bin/pip install --no-cache-dir -r requirements.txt

# Expose the application port
EXPOSE 8000

# Start the application with uvicorn, using the virtual environment's python
CMD ["/venv/bin/uvicorn", "text_rewriter:app", "--host", "0.0.0.0", "--port", "8000"]
