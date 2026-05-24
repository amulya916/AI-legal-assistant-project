# Use official lightweight Python image
FROM python:3.9-slim

# Set environment variables to optimize Python runtime
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=5000

# Set default data paths inside the container
ENV DATABASE_PATH=/app/data/database.db
ENV UPLOAD_FOLDER=/app/uploads

# Set working directory
WORKDIR /app

# Install system dependencies (e.g. build tools if needed for modules)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files into container
COPY . .

# Create directories for persistent volume mounting
RUN mkdir -p /app/data /app/uploads && chmod -R 777 /app/data /app/uploads

# Expose port
EXPOSE 5000

# Run using Gunicorn (4 workers, listening on all interfaces)
CMD ["gunicorn", "--workers", "4", "--bind", "0.0.0.0:5000", "app:app"]
