#!/usr/bin/env bash
# ==============================================================================
# Deploy Agent Gateway & Services to Google Cloud Run
# ==============================================================================

set -e

source .env 2>/dev/null || true

PROJECT_ID=${GCP_PROJECT_ID:-$(gcloud config get-value project 2>/dev/null)}
REGION=${GCP_REGION:-"us-central1"}
SERVICE_NAME="agent-gateway"

if [ -z "$PROJECT_ID" ]; then
    echo "❌ Error: GCP_PROJECT_ID is not set in .env or gcloud configuration."
    exit 1
fi

echo "===================================================================="
echo "🚀 Deploying Agent Service to Google Cloud Run"
echo "Project : $PROJECT_ID"
echo "Region  : $REGION"
echo "Service : $SERVICE_NAME"
echo "===================================================================="

# Build and Deploy to Cloud Run using Google Cloud Buildpack / Dockerfile
gcloud run deploy "$SERVICE_NAME" \
    --source . \
    --project "$PROJECT_ID" \
    --region "$REGION" \
    --platform managed \
    --no-allow-unauthenticated \
    --set-env-vars "GEMINI_MODEL=${GEMINI_MODEL:-gemini-3.7-flash}" \
    --min-instances 0 \
    --max-instances 5 \
    --memory 1Gi \
    --cpu 1

echo "===================================================================="
echo "✅ Deployment Successful!"
echo "===================================================================="
