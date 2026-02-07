#!/bin/bash
#
# deploy.sh - Deploy website to UFES server via SFTP
#
# This script uploads the new website files to http://www.lcad.inf.ufes.br/alberto
#
# IMPORTANT: You must be connected to the departmental VPN before running this script.
#
# Usage:
#   ./deploy.sh [--dry-run]
#
# Options:
#   --dry-run   Show what would be transferred without actually transferring
#
# Prerequisites:
#   - lftp installed (sudo apt install lftp)
#   - Connected to UFES departmental VPN
#   - SSH key or password for lcad@sftp.inf.ufes.br
#

set -e

# Configuration
REMOTE_HOST="sftp.inf.ufes.br"
REMOTE_USER="lcad"
REMOTE_PATH="site/alberto"
LOCAL_SRC_DIR="$(dirname "$0")/src"
DIST_DIR="$(dirname "$0")/dist"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Parse arguments
DRY_RUN=false
for arg in "$@"; do
    case $arg in
        --dry-run)
            DRY_RUN=true
            ;;
    esac
done

if [ "$DRY_RUN" = true ]; then
    echo -e "${YELLOW}=== DRY RUN MODE ===${NC}"
    echo "No files will be transferred."
    echo
fi

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Website Deployment Script${NC}"
echo -e "${BLUE}========================================${NC}"
echo
echo "Target URL: http://www.lcad.inf.ufes.br/alberto"
echo

# Check if lftp is installed
if ! command -v lftp &> /dev/null; then
    echo -e "${RED}Error: lftp is not installed.${NC}"
    echo "Please install it with: sudo apt install lftp"
    exit 1
fi

# Check VPN connection by testing if we can reach the server
echo -e "${YELLOW}Checking VPN connection...${NC}"
if ping -c 1 -W 5 "$REMOTE_HOST" &> /dev/null; then
    echo -e "${GREEN}✓ VPN connection OK${NC}"
else
    echo -e "${RED}✗ Cannot reach $REMOTE_HOST${NC}"
    echo
    echo "Please make sure you are connected to the departmental VPN."
    echo "The server is only accessible through the UFES VPN."
    exit 1
fi

# Prepare dist directory
echo
echo -e "${YELLOW}Preparing website files for deployment...${NC}"

# Create dist directory if it doesn't exist
mkdir -p "$DIST_DIR"

# Clear dist and copy fresh files
rm -rf "$DIST_DIR"/*

# Copy the main page as index.html in the root of dist
cp "$LOCAL_SRC_DIR/alberto/index.html" "$DIST_DIR/index.html"

# Copy assets
cp -r "$LOCAL_SRC_DIR/assets" "$DIST_DIR/"

# Copy data
cp -r "$LOCAL_SRC_DIR/data" "$DIST_DIR/"

echo -e "${GREEN}✓ Files prepared${NC}"

# Count files to be deployed
FILE_COUNT=$(find "$DIST_DIR" -type f | wc -l)
echo "Total files to deploy: $FILE_COUNT"

# Show structure
echo
echo "Files to deploy:"
find "$DIST_DIR" -type f | sed "s|$DIST_DIR/||"

# Deploy
echo
echo -e "${YELLOW}Uploading website files to $REMOTE_HOST...${NC}"
echo "Remote path: /$REMOTE_PATH"
echo

if [ "$DRY_RUN" = true ]; then
    echo "DRY RUN - No files transferred."
else
    # Upload files
    lftp -c "
        set sftp:auto-confirm yes
        set net:timeout 30
        set net:max-retries 3
        open sftp://$REMOTE_USER@$REMOTE_HOST
        mirror --reverse --verbose --parallel=4 \
            --exclude-glob .git* \
            --exclude-glob __pycache__ \
            --exclude-glob *.pyc \
            $DIST_DIR $REMOTE_PATH
        bye
    "
    
    if [ $? -eq 0 ]; then
        echo
        echo -e "${GREEN}========================================${NC}"
        echo -e "${GREEN}  ✓ Deployment completed successfully!${NC}"
        echo -e "${GREEN}========================================${NC}"
        echo
        echo "Website is now live at:"
        echo "  http://www.lcad.inf.ufes.br/alberto"
        echo
    else
        echo
        echo -e "${RED}========================================${NC}"
        echo -e "${RED}  ✗ Deployment failed!${NC}"
        echo -e "${RED}========================================${NC}"
        echo
        echo "Please check the error messages above and try again."
        exit 1
    fi
fi
