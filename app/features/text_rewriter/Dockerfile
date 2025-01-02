# Use Python 3.12 slim image
FROM python:3.12-slim

# Set environment variables for non-interactive installs
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Set working directory inside the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libssl-dev \
    libffi-dev \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements.txt and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && rm -rf /root/.cache

# Copy the application source code into the container
COPY . .

# Create and activate a virtual environment
RUN python3 -m venv /venv \
    && /venv/bin/pip install --no-cache-dir --upgrade pip \
    && /venv/bin/pip install --no-cache-dir -r requirements.txt

# Set the virtual environment as the default Python environment
ENV PATH="/venv/bin:$PATH"

# Expose the application port
EXPOSE 8000

# ENTRYPOINT allows you to run uvicorn, but it can be overridden
ENTRYPOINT ["/venv/bin/uvicorn"]

