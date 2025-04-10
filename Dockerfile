# Use Python 3.9 slim as base image
FROM 3.12-slim-bookworm

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    WORKERS=4 \
    PORT=8000

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create and set working directory
WORKDIR /app

# Install Python dependencies
COPY pyproject.toml ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir .

# Copy application code
COPY . .

# Create a non-root user
RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app
USER appuser

# Run gunicorn with uvicorn workers
CMD gunicorn main:app \
    --bind 0.0.0.0:$PORT \
    --worker-class uvicorn.workers.UvicornWorker \
    --workers $WORKERS \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    --timeout 120

