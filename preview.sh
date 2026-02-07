#!/bin/bash
#
# preview.sh - Preview website locally before deployment
#
# This script starts a local HTTP server to preview the website.
#
# Usage:
#   ./preview.sh [port]
#
# Default port is 8000
#

set -e

PORT="${1:-8000}"
LOCAL_SRC_DIR="$(dirname "$0")/src/alberto"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Local Website Preview${NC}"
echo -e "${BLUE}========================================${NC}"
echo

# Check if the directory exists
if [ ! -d "$LOCAL_SRC_DIR" ]; then
    echo -e "${YELLOW}Error: Directory $LOCAL_SRC_DIR not found${NC}"
    exit 1
fi

# Check if Python is available
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo -e "${YELLOW}Error: Python is not installed.${NC}"
    echo "Please install Python to use this preview server."
    exit 1
fi

echo -e "${GREEN}Starting local server...${NC}"
echo
echo -e "Website will be available at:"
echo -e "  ${BLUE}http://localhost:$PORT${NC}"
echo
echo -e "Press ${YELLOW}Ctrl+C${NC} to stop the server."
echo

# Change to the source directory and start the server
cd "$LOCAL_SRC_DIR"

# Start Python HTTP server
$PYTHON_CMD -m http.server $PORT
