# Kai - AI Backend

This

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. When adding new features, create a branch and then submit a pull request. It is recommended to use the dockerfile for local development.

### Prerequisites

What things you need to install the software and how to install them:

- Docker: Follow the [official Docker installation guide](https://docs.docker.com/get-docker/)

### Building the Docker Image

To build the Docker image, navigate to the directory containing the Dockerfile and run the following command:

```bash
docker build -t kai_ai .
```

### Running the Docker Image
To run the Docker image, use the command:
```bash
docker run -p 8000:8000 kai_ai
```



