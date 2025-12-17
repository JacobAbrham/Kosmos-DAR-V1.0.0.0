# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir pydantic

# Copy the current directory contents into the container at /app
COPY src/agents/hermes /app/src/agents/hermes
COPY src/core /app/src/core

# Set python path to include src
ENV PYTHONPATH=/app/src

# Run main.py when the container launches
CMD ["python", "src/agents/hermes/main.py"]
