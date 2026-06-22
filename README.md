# Air Quality Edge Assistant

An AI-powered air quality assistant that runs on Raspberry Pi 4, Linux, macOS, and Windows. It leverages Gemma 4 E2B (via Ollama) and a flexible, YAML-driven Tool Registry to fetch data from external APIs without direct LLM API calls.

## Architecture
- **Backend**: FastAPI, SQLite (Dockerized)
- **AI Engine**: Ollama running natively (or Docker on capable hosts)
- **UI**: Tkinter Desktop App running natively

## Quick Start (Development on PC)

### 1. Prerequisites
- Docker & Docker Compose
- Python 3.12
- Ollama installed locally

### 2. Pull the LLM Model
```bash
ollama pull gemma:2b
```

### 3. Start the Backend
```bash
docker-compose up --build
```
The FastAPI backend will start at `http://localhost:8000`.

### 4. Start the Desktop UI
Open a new terminal:
```bash
pip install -r desktop/requirements.txt
python -m desktop.ui.app
```

## Deployment on Raspberry Pi

We provide an `install.sh` script optimized for Raspberry Pi OS (ARM64) that installs Docker, Ollama natively, pulls the models, and starts the backend via Docker Compose.

```bash
chmod +x scripts/install.sh
./scripts/install.sh
```

## Adding Tools
To add a new tool, simply update `backend/config/tools.yaml`. No Python code changes are required! The Agent Orchestrator will automatically read the YAML and provide it to the LLM during the tool selection phase.

```yaml
tools:
  - name: my_new_tool
    description: Fetch new data
    endpoint: /my-endpoint
    method: GET
```
