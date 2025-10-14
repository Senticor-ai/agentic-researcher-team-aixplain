#!/bin/bash
# Start the frontend UI server

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Change to the UI directory
cd "$SCRIPT_DIR/ui"

echo "Starting Honeycomb OSINT Frontend UI..."
echo "UI will be available at: http://localhost:5173"
echo ""

# Run the frontend
npm run dev
