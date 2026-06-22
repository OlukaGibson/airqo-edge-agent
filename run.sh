#!/bin/bash

# Exit on any error
set -e

echo "Starting Air Quality Edge Assistant..."

# 1. Start backend services in detached mode
echo "Ensuring backend services are running..."
docker-compose up -d

# 2. Start Ollama model natively if installed (it usually runs as a background service, but we can verify it's up)
if command -v ollama &> /dev/null; then
    # Checking if it's already serving
    if ! curl -s http://localhost:11434/api/tags > /dev/null; then
        echo "Starting Ollama service..."
        ollama serve &
        sleep 3
    fi
    
    # Check if default model exists, pull if missing
    DEFAULT_MODEL="gemma:2b"
    if ! curl -s http://localhost:11434/api/tags | grep -q "\"name\":\"${DEFAULT_MODEL}\""; then
        echo "Model ${DEFAULT_MODEL} not found. Pulling it now..."
        ollama pull ${DEFAULT_MODEL}
    fi
fi

# 3. Activate Virtual Environment and launch UI
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
else
    echo "Virtual environment not found! Please run ./scripts/install.sh first."
    exit 1
fi

echo "Launching Desktop App..."
python -m desktop.ui.app
