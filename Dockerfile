# Use Python 3.9 slim as base image
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    WORKERS=4 \
    PORT=8000

# Install system dependencies
RUN apt-get update && \
apt-get -y install tesseract-ocr

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


EXPOSE $PORT
# Run gunicorn with uvicorn workers
CMD gunicorn main:app \
    --bind 0.0.0.0:$PORT \
    --worker-class uvicorn.workers.UvicornWorker \
    --workers $WORKERS \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    --timeout 120

