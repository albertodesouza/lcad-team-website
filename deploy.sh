#!/bin/bash
#
# deploy.sh - Deploy website to UFES server via SFTP
#
# This script synchronizes the local website files to the remote server.
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
REMOTE_PATH="/site/team"
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
if [ "$1" == "--dry-run" ]; then
    DRY_RUN=true
    echo -e "${YELLOW}=== DRY RUN MODE ===${NC}"
    echo "No files will be transferred."
    echo
fi

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Website Deployment Script${NC}"
echo -e "${BLUE}========================================${NC}"
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
echo -e "${YELLOW}Preparing files for deployment...${NC}"

# Create dist directory if it doesn't exist
mkdir -p "$DIST_DIR"

# Copy source files to dist
echo "Copying files to dist directory..."
rsync -av --delete \
    --exclude '.git' \
    --exclude '.github' \
    --exclude '__pycache__' \
    --exclude '*.pyc' \
    --exclude '.DS_Store' \
    "$LOCAL_SRC_DIR/" "$DIST_DIR/"

# Copy existing team files if they exist (to preserve MediaWiki structure)
if [ -d "$(dirname "$0")/team" ]; then
    echo "Preserving existing MediaWiki files..."
    # Only copy specific directories we want to keep
    for dir in images skins; do
        if [ -d "$(dirname "$0")/team/$dir" ]; then
            mkdir -p "$DIST_DIR/$dir"
            rsync -av "$(dirname "$0")/team/$dir/" "$DIST_DIR/$dir/"
        fi
    done
fi

echo -e "${GREEN}✓ Files prepared${NC}"

# Count files to be deployed
FILE_COUNT=$(find "$DIST_DIR" -type f | wc -l)
echo "Total files to deploy: $FILE_COUNT"

# Deploy
echo
echo -e "${YELLOW}Starting deployment to $REMOTE_HOST...${NC}"
echo "Remote path: $REMOTE_PATH"
echo

if [ "$DRY_RUN" = true ]; then
    # Dry run - just show what would be done
    echo "Files that would be transferred:"
    find "$DIST_DIR" -type f | head -20
    if [ "$FILE_COUNT" -gt 20 ]; then
        echo "... and $((FILE_COUNT - 20)) more files"
    fi
else
    # Actual deployment using lftp
    # Using mirror with --reverse to upload local to remote
    lftp -c "
        set sftp:auto-confirm yes
        set net:timeout 30
        set net:max-retries 3
        open sftp://$REMOTE_USER@$REMOTE_HOST
        mirror --reverse --delete --verbose --parallel=4 \
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
        echo "  http://www.lcad.inf.ufes.br/team/index.php/Prof._Dr._Alberto_Ferreira_De_Souza"
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
