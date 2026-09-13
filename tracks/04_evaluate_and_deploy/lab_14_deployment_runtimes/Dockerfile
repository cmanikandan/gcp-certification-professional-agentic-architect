# This Dockerfile illustrates how a manual Cloud Run deployment might look
# Note: adk deploy cloud_run handles this automatically via Cloud Build

FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PORT=8080
# Expose the API server
CMD ["adk", "api_server", "agent.py", "--port", "8080"]
