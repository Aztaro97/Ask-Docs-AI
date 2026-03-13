#!/bin/bash
# Development environment setup for Ask-Docs

set -e

echo "=== Setting up Ask-Docs Development Environment ==="
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version || { echo "Python 3.11+ required"; exit 1; }

# Check Node version
echo "Checking Node version..."
node --version || { echo "Node 18+ required"; exit 1; }

# Create virtual environment
echo ""
echo "Creating Python virtual environment..."
cd backend
python3 -m venv .venv
source .venv/bin/activate

# Install backend dependencies
echo "Installing backend dependencies..."
pip install -e ".[dev]"

# Install frontend dependencies
echo ""
echo "Installing frontend dependencies..."
cd ../frontend
npm install

# Create data directories
echo ""
echo "Creating data directories..."
cd ..
mkdir -p data/index data/cache docs

# Download models
echo ""
echo "Downloading ML models..."
./scripts/download-models.sh

echo ""
echo "=== Setup Complete! ==="
echo ""
echo "To start development:"
echo "  1. Activate virtualenv: source backend/.venv/bin/activate"
echo "  2. Start Ollama: ollama serve"
echo "  3. Run: make dev"
echo ""
echo "Or use Docker: make docker-up"
