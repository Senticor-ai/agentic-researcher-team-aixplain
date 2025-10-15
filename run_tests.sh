#!/bin/bash
# Comprehensive test runner for Honeycomb OSINT Agent Team System
#
# Usage:
#   ./run_tests.sh              # Run unit tests only (default, fast)
#   ./run_tests.sh unit         # Run unit tests only
#   ./run_tests.sh integration  # Run integration tests (requires backend)
#   ./run_tests.sh e2e          # Run end-to-end tests (requires backend + APIs)
#   ./run_tests.sh all          # Run all tests
#   ./run_tests.sh regression   # Run regression tests
#   ./run_tests.sh coverage     # Run tests with coverage report

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${BLUE}ℹ ${NC}$1"
}

print_success() {
    echo -e "${GREEN}✅ ${NC}$1"
}

print_warning() {
    echo -e "${YELLOW}⚠️  ${NC}$1"
}

print_error() {
    echo -e "${RED}❌ ${NC}$1"
}

# Function to check if backend is running
check_backend() {
    if curl -s http://localhost:8080/api/v1/health > /dev/null 2>&1; then
        return 0
    elif curl -s http://localhost:8000/api/v1/health > /dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Get test type from argument (default: unit)
TEST_TYPE="${1:-unit}"

echo ""
print_info "Honeycomb OSINT Test Runner"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

case "$TEST_TYPE" in
    unit)
        print_info "Running UNIT tests (fast, no external dependencies)"
        echo ""
        poetry run pytest -m "unit" tests/
        ;;
    
    integration)
        print_info "Running INTEGRATION tests (requires backend)"
        echo ""
        
        if ! check_backend; then
            print_error "Backend is not running!"
            echo ""
            print_info "Please start the backend first:"
            echo "  ./start-backend.sh"
            echo ""
            exit 1
        fi
        
        print_success "Backend is running"
        echo ""
        poetry run pytest -m "integration" tests/
        ;;
    
    e2e)
        print_info "Running END-TO-END tests (requires backend + external APIs)"
        echo ""
        
        if ! check_backend; then
            print_error "Backend is not running!"
            echo ""
            print_info "Please start the backend first:"
            echo "  ./start-backend.sh"
            echo ""
            exit 1
        fi
        
        print_success "Backend is running"
        echo ""
        poetry run pytest -m "e2e" tests/
        ;;
    
    all)
        print_info "Running ALL tests"
        echo ""
        
        if ! check_backend; then
            print_warning "Backend is not running - integration/e2e tests will be skipped"
            echo ""
            poetry run pytest -m "unit" tests/
        else
            print_success "Backend is running"
            echo ""
            poetry run pytest tests/
        fi
        ;;
    
    regression)
        print_info "Running REGRESSION tests"
        echo ""
        poetry run pytest -m "regression" tests/
        ;;
    
    coverage)
        print_info "Running tests with COVERAGE report"
        echo ""
        
        # Check if pytest-cov is installed
        if ! poetry run python -c "import pytest_cov" 2>/dev/null; then
            print_warning "pytest-cov not installed, installing..."
            poetry add --group dev pytest-cov
        fi
        
        poetry run pytest --cov=api --cov-report=html --cov-report=term tests/
        
        print_success "Coverage report generated in htmlcov/index.html"
        ;;
    
    *)
        print_error "Unknown test type: $TEST_TYPE"
        echo ""
        echo "Usage:"
        echo "  ./run_tests.sh              # Run unit tests (default)"
        echo "  ./run_tests.sh unit         # Run unit tests only"
        echo "  ./run_tests.sh integration  # Run integration tests"
        echo "  ./run_tests.sh e2e          # Run end-to-end tests"
        echo "  ./run_tests.sh all          # Run all tests"
        echo "  ./run_tests.sh regression   # Run regression tests"
        echo "  ./run_tests.sh coverage     # Run with coverage report"
        echo ""
        exit 1
        ;;
esac

echo ""
print_success "Tests completed!"
echo ""
