#!/bin/bash
# Quick script to run integration tests
# Usage: ./tests/RUN_INTEGRATION_TESTS.sh [test_name]

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}Agent Workflow Integration Tests${NC}"
echo -e "${GREEN}================================${NC}"
echo ""

# Check for API key
if [ -z "$TEAM_API_KEY" ] && [ ! -f .env ]; then
    echo -e "${RED}ERROR: TEAM_API_KEY not found${NC}"
    echo ""
    echo "Please set your API key:"
    echo "  1. Create .env file: echo 'TEAM_API_KEY=your_key' > .env"
    echo "  2. Or export: export TEAM_API_KEY=your_key"
    echo ""
    exit 1
fi

# Load .env if it exists
if [ -f .env ]; then
    echo -e "${YELLOW}Loading environment from .env${NC}"
    export $(cat .env | grep -v '^#' | xargs)
fi

# Check if specific test requested
if [ -n "$1" ]; then
    TEST_NAME="$1"
    echo -e "${YELLOW}Running specific test: ${TEST_NAME}${NC}"
    echo ""
    pytest tests/test_agent_workflow_integration.py::TestAgentWorkflowIntegration::${TEST_NAME} -v -s --log-cli-level=INFO
else
    echo -e "${YELLOW}Running all integration tests${NC}"
    echo ""
    echo "Available tests:"
    echo "  - test_person_entity_workflow"
    echo "  - test_organization_entity_workflow"
    echo "  - test_event_entity_workflow"
    echo "  - test_policy_entity_workflow"
    echo "  - test_validation_metrics"
    echo ""
    echo -e "${YELLOW}Starting in 3 seconds... (Ctrl+C to cancel)${NC}"
    sleep 3
    echo ""
    pytest tests/test_agent_workflow_integration.py -v -s --log-cli-level=INFO
fi

echo ""
echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}Integration tests complete!${NC}"
echo -e "${GREEN}================================${NC}"
