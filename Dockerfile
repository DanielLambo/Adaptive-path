# Dockerfile for the Adaptive Learning Path Generator

# --- Base Stage ---
# Use a slim Python image for a smaller footprint.
FROM python:3.11-slim

# --- Environment Variables ---
# Set the working directory in the container.
WORKDIR /app

# Prevents Python from writing .pyc files to disc.
ENV PYTHONDONTWRITEBYTECODE 1
# Ensures Python output is sent straight to the terminal without buffering.
ENV PYTHONUNBUFFERED 1

# --- Dependency Installation ---
# Copy only the requirements file first to leverage Docker's layer caching.
# This layer will only be rebuilt if requirements.txt changes.
COPY requirements.txt .

# Install the runtime dependencies.
# We don't install dev dependencies in the production image.
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# --- Application Code ---
# Copy the rest of the application code into the container.
COPY ./app /app/app

# Note: The 'models' directory is intentionally not copied.
# In a real-world scenario, the model artifacts should be downloaded
# from a model registry (like S3, GCS, or MLFlow) during the container's
# startup sequence, not baked into the image.

# --- Port Exposure ---
# Expose the port the application will run on.
EXPOSE 8000

# --- Startup Command ---
# Command to run the application using Uvicorn.
# The host 0.0.0.0 is necessary to accept connections from outside the container.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
