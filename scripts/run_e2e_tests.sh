#!/bin/bash
# End-to-end integration test runner
# Ensures backend is running before executing tests

set -e

echo "🔍 Checking if backend is running..."

# Check if backend is accessible
if ! curl -s http://localhost:8000/api/v1/health > /dev/null; then
    echo "❌ Backend is not running on http://localhost:8000"
    echo ""
    echo "Please start the backend first:"
    echo "  poetry run uvicorn api.main:app --reload --port 8000"
    echo ""
    exit 1
fi

echo "✅ Backend is running"
echo ""
echo "🧪 Running end-to-end integration tests..."
echo ""

# Run the tests
poetry run pytest tests/test_e2e_integration.py -v

echo ""
echo "✅ All tests completed!"
