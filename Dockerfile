# Use official Python runtime as base image
FROM python:3.12-slim

# Set environment variables
# PYTHONUNBUFFERED=1 ensures Python output is sent straight to logs (not buffered)
ENV PYTHONUNBUFFERED=1 \
    # PIP_NO_CACHE_DIR=1 reduces image size by not caching pip packages
    PIP_NO_CACHE_DIR=1

# Set work directory inside container
WORKDIR /app

# Install system dependencies required by psycopg2 (PostgreSQL adapter) and other packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements.txt from host to container
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy entire project from host to container
COPY . .

# Collect static files (for production)
RUN python manage.py collectstatic --noinput

# Expose port 8000 (Django dev server)
EXPOSE 8000

# Default command: run Django development server
# Can be overridden by docker-compose to run celery worker, celery beat, etc.
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
