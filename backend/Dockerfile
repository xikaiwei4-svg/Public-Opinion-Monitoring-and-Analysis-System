﻿# backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for torch, jieba, and mysql client
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    curl \
    libmariadb-dev-compat \
    libmariadb-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire backend directory
COPY . .

# Expose port
EXPOSE 8000

# Use uvicorn with 4 workers for production
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
