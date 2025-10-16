#!/bin/bash
# Start the backend API server in development mode with auto-reload and verbose logging

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Change to the script directory (project root)
cd "$SCRIPT_DIR"

echo "Starting Honeycomb OSINT Backend API (Development Mode)..."
echo "API will be available at: http://localhost:8080"
echo "API Docs will be available at: http://localhost:8080/docs"
echo "Auto-reload: Enabled (will restart on file changes)"
echo "Log level: DEBUG"
echo ""

# Run the backend using uvicorn with auto-reload and debug logging
poetry run uvicorn api.main:app --reload --host 0.0.0.0 --port 8080 --log-level debug
