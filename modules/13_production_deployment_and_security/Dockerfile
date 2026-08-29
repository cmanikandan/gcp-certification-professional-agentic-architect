# Google Cloud Production Agent Container for Cloud Run
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Set default environment variables
ENV PORT=8080
ENV GEMINI_MODEL=gemini-3.7-flash
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8080/healthz || exit 1

# Start FastAPI server via Uvicorn
CMD ["uvicorn", "modules.13_production_deployment_and_security.deploy_cloud_run:app", "--host", "0.0.0.0", "--port", "8080"]
