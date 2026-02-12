#!/bin/bash

# LinkBeam Integration Test Script

echo "🧪 LinkBeam Integration Test Suite"
echo "=================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

PASSED=0
FAILED=0

# Test function
test_endpoint() {
    local name=$1
    local url=$2
    local expected=$3
    
    echo -n "Testing $name... "
    
    response=$(curl -s "$url")
    
    if echo "$response" | grep -q "$expected"; then
        echo -e "${GREEN}✓ PASSED${NC}"
        ((PASSED++))
    else
        echo -e "${RED}✗ FAILED${NC}"
        echo "  Expected: $expected"
        echo "  Got: $response"
        ((FAILED++))
    fi
}

# Start backend
echo "Starting backend server..."
cd backend
python app.py > /tmp/test_backend.log 2>&1 &
BACKEND_PID=$!
cd ..

# Wait for server to start
sleep 3

# Run tests
echo ""
echo "Running API Tests:"
echo "------------------"

test_endpoint "Health Check" "http://localhost:5000/api/health" "ok"
test_endpoint "Device Info" "http://localhost:5000/api/device/info" "device_id"
test_endpoint "Device List" "http://localhost:5000/api/devices" "\\["
test_endpoint "Files List" "http://localhost:5000/api/files" "\\["

# Test file upload
echo -n "Testing File Upload... "
echo "Test content" > /tmp/test_upload.txt
response=$(curl -s -X POST -F "file=@/tmp/test_upload.txt" http://localhost:5000/api/upload)
if echo "$response" | grep -q "success"; then
    echo -e "${GREEN}✓ PASSED${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ FAILED${NC}"
    ((FAILED++))
fi

# Test file download
echo -n "Testing File Download... "
response=$(curl -s -o /tmp/test_download.txt -w "%{http_code}" http://localhost:5000/api/download/test_upload.txt)
if [ "$response" = "200" ]; then
    echo -e "${GREEN}✓ PASSED${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ FAILED${NC}"
    ((FAILED++))
fi

# Frontend build check
echo ""
echo "Frontend Build Check:"
echo "--------------------"
echo -n "Checking React build... "
if [ -d "frontend/build" ]; then
    echo -e "${GREEN}✓ PASSED${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ FAILED${NC}"
    ((FAILED++))
fi

# Cleanup
kill $BACKEND_PID 2>/dev/null
rm -f /tmp/test_upload.txt /tmp/test_download.txt

# Summary
echo ""
echo "=================================="
echo "Test Summary:"
echo "  Passed: ${GREEN}$PASSED${NC}"
echo "  Failed: ${RED}$FAILED${NC}"
echo "=================================="

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}All tests passed! ✓${NC}"
    exit 0
else
    echo -e "${RED}Some tests failed! ✗${NC}"
    exit 1
fi
