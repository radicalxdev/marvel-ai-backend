# Kai AI Platform

![Static Badge](https://img.shields.io/badge/v3.10.12-blue?logo=python&logoColor=yellow&labelColor=gray)
![Static Badge](https://img.shields.io/badge/Gemini%201.0-blue?logo=googlegemini&logoColor=blue&labelColor=gray)
![Static Badge](https://img.shields.io/badge/Vertex%20AI-blue?logo=googlecloud&logoColor=white&labelColor=gray)
![Static Badge](https://img.shields.io/badge/FastAPI-blue?logo=fastapi&logoColor=white&labelColor=gray)

## Table of Contents

- [Architecture](#Architecture)
- [Folder Structure](#folder-structure)
- [Setup](#Setup)
- [Local Development](#local-development)
- [Contributing](#Contributing)
  ![Architectural Diagram](diagram.png)

## Folder Structure

```plaintext
backend/
├── app/                     # Contains the main application code
│   ├── Api/                 # Contains the API router for handling requests
│   │   └── router.py        # Endpoints for FastAPI to test features and handle incoming requests
│   ├── chats/               # Handles chat functionalities
│   ├── Features/            # Contains feature-specific modules
│   │   ├── Feature1/
│   │   │   ├── core.py
│   │   │   ├── tools.py
│   │   │   ├── Prompt/
│   │   │   └── metadata.json
│   │   ├── Feature2/
│   │   │   ├── core.py
│   │   │   ├── tools.py
│   │   │   ├── Prompt/
│   │   │   └── metadata.json
│   ├── services/            # Contains service modules
│   ├── utils/               # Contains utility modules
│   ├── app.yaml             # Application configuration file
│   ├── Dependencies.py      # Dependency management
│   ├── Main.py              # Main entry point for the application
│   └── requirements.txt     # Python dependencies
├── Dockerfile               # Dockerfile for containerizing the application
└── README.md                # Documentation file
```

## Install all the necessary libraries:

### Navigate to the app directory

```bash
cd backend/app
```

### Create and activate Virtual Environment

```bash
python -m venv env
source env/bin/activate
```

```bash
pip install -r requirements.txt
```

## To Run Locally and Test

## Prerequisites

- A Google Cloud account.
- Access to the Google Cloud Platform console.

## Steps for Authentication Setup

### Step 1: Create a Google Cloud Project

1. Navigate to the [Google Cloud Console](https://console.cloud.google.com/) and create a new project.

### Step 2: Enable the Google Cloud APIs

1. Enable the following APIs:
   - VertexAI

### Step 3: Create a new AI Studio API Key

1. Navigate to the [AI Studio API Key page](https://aistudio.google.com/app/u/1/apikey) and create a new API key. This will connect with your Google Cloud Project.

### Step 4: Create a new .env and store the API Key

1. Create a new file called `.env` in the root of the project.
2. Copy the contents of the `.env.example` file into the `.env` file.
3. Replace the placeholder values with your API key and project ID.
4. Set the `ENV_TYPE` variable to `dev`.

### Step 4: Run the Application with Local Shell Script

1. Run the following command to start the application:

```bash
./local-start.sh
```

# Docker Setup Guide

## Overview

This guide is designed to help contributors set up and run the backend service using Docker. Follow these steps to ensure that your development environment is configured correctly.

## Prerequisites

Before you start, ensure you have the following installed:

- Docker
- Python

## Installation Instructions

### 1. Build the Docker Image

Navigate to the project's root directory and build the Docker image. Typically, this is done with the following command:

```Bash
docker build -t <image_name> .
```

### 3 Run the Docker Container

Run the Docker container using the following command:

```bash
docker run -p 8000:8000 <image_name>
```

This command starts a detached container that maps port 8000 of the container to port 8000 on the host.

## Environment Variables

The Docker container uses several key environment variables:

- ENV_TYPE set to "dev" for development.
- PROJECT_ID specifies your Google Cloud project ID.
- It is possible to enable LangChain tracing by setting the following environment variables. More information can be found on LangSmith
  `LANGCHAIN_TRACING_V2`
  `LANGCHAIN_ENDPOINT`
  `LANGCHAIN_API_KEY`
  `LANGCHAIN_PROJECT`
- Ensure these variables are correctly configured in a .env file.

## Accessing the Application

You can access the backend by visiting:

```Bash
http://localhost:8000/docs
```

After your container starts, you should see the FastAPI landing page, indicating that the application is running successfully.
