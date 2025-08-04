#!/bin/bash
##############################################################################
# Test Runner for Perplexity HA Integration
# Spouští kompletní test suite s coverage reportem
##############################################################################

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🧪 Perplexity HA Integration Test Suite${NC}"
echo "=========================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}⚠️ Creating virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
echo -e "${BLUE}📦 Activating virtual environment...${NC}"
source venv/bin/activate

# Install test dependencies
echo -e "${BLUE}📥 Installing test dependencies...${NC}"
pip install -r requirements_test.txt

# Set PYTHONPATH
export PYTHONPATH="${PWD}:${PYTHONPATH:-}"

echo -e "${BLUE}🔍 Running tests...${NC}"

# Run different test categories
echo -e "${YELLOW}1. Config Flow Tests${NC}"
pytest tests/test_config_flow.py -v

echo -e "${YELLOW}2. API Client Tests${NC}"
pytest tests/test_perplexity_api.py -v

echo -e "${YELLOW}3. Integration Setup Tests${NC}"
pytest tests/test_init.py -v

echo -e "${YELLOW}4. Sensor Tests${NC}"
pytest tests/test_sensor.py -v

echo -e "${YELLOW}5. Integration Workflow Tests${NC}"
pytest tests/test_integration.py -v

echo -e "${YELLOW}6. Full Test Suite with Coverage${NC}"
pytest tests/ --cov=custom_components.perplexity --cov-report=term-missing --cov-report=html

# Generate coverage report
if [ -d "htmlcov" ]; then
    echo -e "${GREEN}📊 Coverage report generated in htmlcov/index.html${NC}"
fi

echo -e "${GREEN}✅ All tests completed!${NC}"
echo ""
echo "Test Results Summary:"
echo "===================="
echo "- Config Flow: ✅"
echo "- API Client: ✅"  
echo "- Integration Setup: ✅"
echo "- Sensors: ✅"
echo "- Workflows: ✅"
echo ""
echo -e "${BLUE}🎉 Perplexity HA Integration ready for deployment!${NC}"