#!/bin/bash
# End-to-end integration test runner
# Ensures backend is running before executing tests

set -e

echo "🔍 Checking if backend is running..."

# Check if backend is accessible (try both 8080 and 8000)
if curl -s http://localhost:8080/api/v1/health > /dev/null; then
    export API_PORT=8080
    echo "✅ Backend is running on port 8080"
elif curl -s http://localhost:8000/api/v1/health > /dev/null; then
    export API_PORT=8000
    echo "✅ Backend is running on port 8000"
else
    echo "❌ Backend is not running on http://localhost:8080 or http://localhost:8000"
    echo ""
    echo "Please start the backend first:"
    echo "  ./start-backend.sh"
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
