#!/usr/bin/env bash
# ==============================================================================
# Google Cloud Certified Professional Agentic Architect — Resource Cleanup Script
# ==============================================================================

set -e

# Load environment variables
if [ -f ".env" ]; then
    source .env
fi

PROJECT_ID=${GCP_PROJECT_ID:-$(gcloud config get-value project 2>/dev/null || echo "")}
REGION=${GCP_REGION:-"us-central1"}
SERVICE_NAME="agent-gateway"
BUCKET_NAME=${GCS_BUCKET_NAME:-""}

echo "===================================================================="
echo "🧹 Google Cloud Agentic Architect — Resource Teardown"
echo "===================================================================="
echo "Target GCP Project : ${PROJECT_ID:-'Not set'}"
echo "Target Region      : ${REGION}"
echo "Target Service     : ${SERVICE_NAME}"
echo "Target Bucket      : ${BUCKET_NAME:-'None specified'}"
echo "===================================================================="

if [ -z "$PROJECT_ID" ]; then
    echo "⚠️ Warning: GCP_PROJECT_ID is not configured. Skipping remote GCP teardown."
    echo "To configure, set GCP_PROJECT_ID in .env or run 'gcloud config set project <PROJECT_ID>'."
else
    read -p "⚠️ Are you sure you want to delete deployed lab resources in project '$PROJECT_ID'? (y/N): " CONFIRM
    if [[ "$CONFIRM" =~ ^[Yy]$ ]]; then
        echo ""
        echo "1. Deleting Cloud Run Agent Gateway Service..."
        if gcloud run services describe "$SERVICE_NAME" --project "$PROJECT_ID" --region "$REGION" &>/dev/null; then
            gcloud run services delete "$SERVICE_NAME" --project "$PROJECT_ID" --region "$REGION" --quiet
            echo "✅ Cloud Run service '$SERVICE_NAME' deleted."
        else
            echo "ℹ️ Cloud Run service '$SERVICE_NAME' not found or already deleted."
        fi

        echo ""
        echo "2. Deleting Cloud Storage Lab Artifact Buckets..."
        if [ -n "$BUCKET_NAME" ]; then
            if gcloud storage buckets describe "gs://${BUCKET_NAME}" --project "$PROJECT_ID" &>/dev/null; then
                gcloud storage rm --recursive "gs://${BUCKET_NAME}" --quiet
                echo "✅ Bucket 'gs://${BUCKET_NAME}' and all contents deleted."
            else
                echo "ℹ️ Bucket 'gs://${BUCKET_NAME}' not found."
            fi
        else
            echo "ℹ️ No GCS_BUCKET_NAME specified in .env, skipping GCS bucket deletion."
        fi

        echo ""
        echo "3. Cleaning up local cache and temporary test artifacts..."
    fi
fi

# Run each lab's scoped, idempotent local cleanup contract.
for LAB_CLEANUP in tracks/[0-9][0-9]_*/lab_[0-9][0-9]_*/cleanup.sh; do
    [ -f "$LAB_CLEANUP" ] || continue
    bash "$LAB_CLEANUP"
done

if [ -d ".pytest_cache" ]; then
    rm -rf -- ".pytest_cache"
fi
rm -f -- agent_memory_cache.json vector_index_cache.bin ./*.log 2>/dev/null || true

echo "✅ Local test caches, SQLite temp databases, and logs cleaned up."
echo "===================================================================="
echo "🎉 Teardown commands completed. Review Billing and Asset Inventory to confirm no live lab resources remain."
echo "===================================================================="
