#!/bin/bash
# Script to run end-to-end integration tests for the MCP server
# This script checks if the backend is running and runs the e2e tests

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
BACKEND_URL="${FASTAPI_BASE_URL:-http://localhost:8000}"
BACKEND_HEALTH_ENDPOINT="${BACKEND_URL}/health"
MAX_WAIT=30  # Maximum seconds to wait for backend

echo "=========================================="
echo "MCP Server E2E Integration Tests"
echo "=========================================="
echo ""

# Function to check if backend is running
check_backend() {
    echo -n "Checking if backend is available at ${BACKEND_URL}... "
    
    if curl -s -f "${BACKEND_HEALTH_ENDPOINT}" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Backend is running${NC}"
        return 0
    else
        echo -e "${RED}✗ Backend is not available${NC}"
        return 1
    fi
}

# Function to wait for backend to start
wait_for_backend() {
    echo "Waiting for backend to start (max ${MAX_WAIT}s)..."
    
    for i in $(seq 1 $MAX_WAIT); do
        if curl -s -f "${BACKEND_HEALTH_ENDPOINT}" > /dev/null 2>&1; then
            echo -e "${GREEN}✓ Backend is ready${NC}"
            return 0
        fi
        echo -n "."
        sleep 1
    done
    
    echo ""
    echo -e "${RED}✗ Backend did not start within ${MAX_WAIT} seconds${NC}"
    return 1
}

# Check if backend is already running
if ! check_backend; then
    echo ""
    echo -e "${YELLOW}Backend is not running. Would you like to start it? (y/n)${NC}"
    read -r response
    
    if [[ "$response" =~ ^[Yy]$ ]]; then
        echo "Starting backend..."
        
        # Check if start script exists
        if [ -f "../start-backend.sh" ]; then
            # Start backend in background
            (cd .. && ./start-backend.sh > /dev/null 2>&1 &)
            
            # Wait for it to be ready
            if ! wait_for_backend; then
                echo -e "${RED}Failed to start backend. Please start it manually:${NC}"
                echo "  cd .. && ./start-backend.sh"
                exit 1
            fi
        else
            echo -e "${RED}Backend start script not found at ../start-backend.sh${NC}"
            echo "Please start the backend manually and run this script again."
            exit 1
        fi
    else
        echo ""
        echo -e "${YELLOW}Please start the backend manually:${NC}"
        echo "  cd .. && ./start-backend.sh"
        echo ""
        echo "Then run this script again."
        exit 1
    fi
fi

echo ""
echo "=========================================="
echo "Running E2E Tests"
echo "=========================================="
echo ""

# Parse command line arguments
TEST_ARGS=""
VERBOSE="-v"

while [[ $# -gt 0 ]]; do
    case $1 in
        --class)
            TEST_ARGS="tests/test_e2e_integration.py::$2"
            shift 2
            ;;
        --test)
            TEST_ARGS="tests/test_e2e_integration.py::$2"
            shift 2
            ;;
        --quick)
            # Run only fast tests (exclude full workflow)
            TEST_ARGS="tests/test_e2e_integration.py -k 'not test_complete_workflow_success'"
            shift
            ;;
        --full)
            # Run only full workflow test
            TEST_ARGS="tests/test_e2e_integration.py::TestFullWorkflow::test_complete_workflow_success"
            shift
            ;;
        -q|--quiet)
            VERBOSE=""
            shift
            ;;
        -vv)
            VERBOSE="-vv"
            shift
            ;;
        -s)
            VERBOSE="${VERBOSE} -s"
            shift
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            echo ""
            echo "Usage: $0 [options]"
            echo ""
            echo "Options:"
            echo "  --class <ClassName>     Run specific test class"
            echo "  --test <TestName>       Run specific test"
            echo "  --quick                 Run only fast tests (skip full workflow)"
            echo "  --full                  Run only full workflow test"
            echo "  -q, --quiet             Quiet output"
            echo "  -vv                     Very verbose output"
            echo "  -s                      Show print statements"
            echo ""
            echo "Examples:"
            echo "  $0                                    # Run all e2e tests"
            echo "  $0 --quick                            # Run fast tests only"
            echo "  $0 --full                             # Run full workflow only"
            echo "  $0 --class TestSpawnAgentTeam         # Run spawn tests"
            echo "  $0 --test TestFullWorkflow::test_complete_workflow_success"
            exit 1
            ;;
    esac
done

# Set default test path if none specified
if [ -z "$TEST_ARGS" ]; then
    TEST_ARGS="tests/test_e2e_integration.py"
fi

# Run the tests
echo "Running: pytest ${TEST_ARGS} ${VERBOSE} -m e2e"
echo ""

cd "$(dirname "$0")"

if pytest ${TEST_ARGS} ${VERBOSE} -m e2e; then
    echo ""
    echo "=========================================="
    echo -e "${GREEN}✓ All E2E tests passed!${NC}"
    echo "=========================================="
    exit 0
else
    echo ""
    echo "=========================================="
    echo -e "${RED}✗ Some E2E tests failed${NC}"
    echo "=========================================="
    exit 1
fi
