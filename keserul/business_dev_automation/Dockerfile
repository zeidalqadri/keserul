FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for potential native packages
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better Docker layer caching
COPY optimizer_api/requirements.txt ./requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire business_dev_automation directory
COPY . ./business_dev_automation/

# Set PYTHONPATH to include the app root
ENV PYTHONPATH=/app

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash app && chown -R app:app /app
USER app

# Use PORT environment variable with default fallback
EXPOSE 8000

CMD ["sh", "-c", "uvicorn business_dev_automation.optimizer_api.main:app --host 0.0.0.0 --port ${PORT:-8000}"] 