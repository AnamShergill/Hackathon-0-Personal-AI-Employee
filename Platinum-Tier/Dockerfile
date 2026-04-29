# Platinum Tier - Docker Image
# For Cloud VM deployment

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p Vault Logs/cloud Logs/local

# Set Python path
ENV PYTHONPATH=/app

# Default command (can be overridden in docker-compose.yml)
CMD ["python", "Actions/cloud_agent.py"]
