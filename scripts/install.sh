#!/bin/bash

# Exit on any error
set -e

echo "=========================================="
echo "Installing Air Quality Edge Assistant"
echo "=========================================="

# 1. Install prerequisites (Debian/Ubuntu/Raspberry Pi OS)
if command -v apt-get &> /dev/null; then
    echo "Installing system prerequisites..."
    sudo apt-get update
    sudo apt-get install -y python3-venv python3-tk
fi

# 2. Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Docker not found. Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    echo "Docker installed. Note: You may need to log out and log back in for group changes to take effect."
else
    echo "Docker is already installed."
fi

# 3. Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "Docker Compose not found. Installing..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
else
    echo "Docker Compose is already installed."
fi

# 4. Install Ollama natively for better performance on Raspberry Pi
if ! command -v ollama &> /dev/null; then
    echo "Installing Ollama natively..."
    curl -fsSL https://ollama.com/install.sh | sh
else
    echo "Ollama is already installed."
fi

# 5. Pull the Gemma model
echo "Pulling the specified Gemma model (gemma:2b)..."
ollama pull gemma:2b

# 6. Start the backend services
echo "Starting FastAPI backend services via Docker Compose..."
docker-compose up -d --build

# 7. Setup Python Virtual Environment for the UI
echo "Setting up Python Virtual Environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install -r requirements.txt
pip install -r desktop/requirements.txt

# 8. Create Linux Desktop Shortcut (if on Linux with a Desktop Environment)
if [ -d "$HOME/Desktop" ]; then
    echo "Creating Desktop shortcut..."
    cat <<EOF > "$HOME/Desktop/AirQoAssistant.desktop"
[Desktop Entry]
Version=1.0
Name=Air Quality Assistant
Comment=Launch the Air Quality Edge AI Agent
Exec=bash -c 'cd $(pwd) && ./run.sh'
Terminal=true
Type=Application
Categories=Utility;
EOF
    chmod +x "$HOME/Desktop/AirQoAssistant.desktop"
fi

echo "=========================================="
echo "Installation Complete!"
echo "Backend is running on http://localhost:8000"
echo "Ollama is running on http://localhost:11434"
echo ""
echo "To start the application, simply run:"
echo "./run.sh"
echo "=========================================="
