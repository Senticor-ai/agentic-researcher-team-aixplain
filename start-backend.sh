#!/bin/bash
# Start the backend API server

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Change to the script directory (project root)
cd "$SCRIPT_DIR"

echo "Starting Honeycomb OSINT Backend API..."
echo "API will be available at: http://localhost:8080"
echo "API Docs will be available at: http://localhost:8080/docs"
echo ""

# Run the backend using poetry
poetry run python -m api.main
