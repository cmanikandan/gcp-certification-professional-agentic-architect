#!/usr/bin/env bash
# ==============================================================================
# Google Cloud Certified Professional Agentic Architect — Environment Bootstrap
# ==============================================================================

set -e

echo "===================================================================="
echo "🚀 Setting up Python Environment for Agentic Architect Labs..."
echo "===================================================================="

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed. Please install Python 3.10+."
    exit 1
fi

echo "Python Version: $(python3 --version)"

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment in .venv..."
    python3 -m venv .venv
fi

# Activate virtual environment
source .venv/bin/activate

# Upgrade pip and install requirements
echo "Installing dependencies from requirements.txt..."
pip install --upgrade pip
pip install -r requirements.txt

# Copy .env.example if .env does not exist
if [ ! -f ".env" ]; then
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo "⚠️ Please update .env with your GCP_PROJECT_ID and GEMINI_API_KEY."
fi

echo "===================================================================="
echo "✅ Setup Complete! Run 'python3 cli.py' to begin."
echo "===================================================================="
