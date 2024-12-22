FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the app source code
COPY . .

# Expose the application port
EXPOSE 8000

# Start the application
CMD ["uvicorn", "text_rewriter:app", "--host", "0.0.0.0", "--port", "8000"]
