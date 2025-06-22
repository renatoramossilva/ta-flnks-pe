# Use the official Python 3.12 slim image as the base image
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the application code into the container
COPY . ./

# Set environment variables for better behavior and configuration
ENV POETRY_VIRTUALENVS_CREATE=false \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Install system dependencies required for the application
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     git \
#     build-essential \
#     curl \
#     libnss3 \
#     libgdk-pixbuf2.0-0 \
#     libatk-bridge2.0-0 \
#     libatk1.0-0 \
#     libcups2 \
#     libx11-xcb1 \
#     libxcomposite1 \
#     libxdamage1 \
#     libxrandr2 \
#     xdg-utils \
#     libxkbcommon0 \
#     libasound2 \
#     libgbm1 \
#     xvfb \
#     && apt-get clean \
#     && rm -rf /var/lib/apt/lists/*

# Copy the .netrc file for authentication and set appropriate permissions
# COPY .netrc /root/.netrc
# RUN chmod 600 /root/.netrc

# Install Poetry and install project dependencies
# RUN pip install --no-cache-dir poetry \
#     && poetry install --no-root
#    && playwright install chromium

# Expose the application port
EXPOSE 3000

# Define the command to run the application
CMD ["uvicorn", "app.main:app", "--host=0.0.0.0", "--port=3000", "--reload"]
