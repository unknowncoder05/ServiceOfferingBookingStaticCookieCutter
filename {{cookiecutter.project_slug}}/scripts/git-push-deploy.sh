#!/bin/bash
# Git push with automatic deployment
# This script pushes to remote and then automatically deploys changes

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Load configuration
CONFIG_FILE="$PROJECT_ROOT/.deploy-config"
if [ -f "$CONFIG_FILE" ]; then
    source "$CONFIG_FILE"
else
    # Defaults
    AUTO_DEPLOY_ENABLED=true
    AUTO_DEPLOY_FRONTEND=true
    AUTO_DEPLOY_BACKEND=true
    AUTO_DEPLOY_INFRASTRUCTURE=false
    REQUIRE_CONFIRMATION=false
    DEPLOY_BRANCH="main"
    VERBOSE=true
fi

# Load environment variables if .env exists
if [ -f "$PROJECT_ROOT/.env" ]; then
    source "$PROJECT_ROOT/.env"
fi

echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}   Git Push + Auto Deploy${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""

# Get current branch
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
echo -e "${BLUE}Current branch: ${CURRENT_BRANCH}${NC}"

# Check if we should deploy on this branch
if [ -n "$DEPLOY_BRANCH" ] && [ "$CURRENT_BRANCH" != "$DEPLOY_BRANCH" ]; then
    echo -e "${YELLOW}⚠️  Auto-deploy only enabled for '${DEPLOY_BRANCH}' branch${NC}"
    echo "Pushing without deployment..."
    git push "$@"
    exit 0
fi

# Save commit before push for comparison
COMMIT_BEFORE_PUSH=$(git rev-parse HEAD)

# Push to remote
echo -e "${BLUE}📤 Pushing to remote...${NC}"
echo ""

if git push "$@"; then
    echo ""
    echo -e "${GREEN}✅ Push successful${NC}"
else
    echo ""
    echo -e "${RED}❌ Push failed${NC}"
    exit 1
fi

# Check if auto-deploy is enabled
if [ "$AUTO_DEPLOY_ENABLED" != "true" ]; then
    echo -e "${YELLOW}Auto-deploy is disabled in .deploy-config${NC}"
    exit 0
fi

echo ""
echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}   Automatic Deployment${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""

# Get last deployed commit
LAST_DEPLOY_FILE="$PROJECT_ROOT/.last-deploy"
if [ -f "$LAST_DEPLOY_FILE" ]; then
    LAST_DEPLOY=$(cat "$LAST_DEPLOY_FILE")
    echo -e "${BLUE}Last deployment: ${LAST_DEPLOY:0:8}${NC}"
else
    LAST_DEPLOY=""
    echo -e "${YELLOW}No previous deployment found${NC}"
fi

CURRENT_COMMIT=$(git rev-parse HEAD)
echo -e "${BLUE}Current commit: ${CURRENT_COMMIT:0:8}${NC}"
echo ""

# Detect changes
if [ -n "$LAST_DEPLOY" ]; then
    FRONTEND_CHANGED=$(git diff --name-only $LAST_DEPLOY HEAD | grep -c "^frontend/" || true)
    BACKEND_CHANGED=$(git diff --name-only $LAST_DEPLOY HEAD | grep -c "^BackEndApi/" || true)
    INFRA_CHANGED=$(git diff --name-only $LAST_DEPLOY HEAD | grep -c "^terraform/" || true)
else
    # First deployment - consider everything changed
    FRONTEND_CHANGED=1
    BACKEND_CHANGED=1
    INFRA_CHANGED=0  # Don't auto-deploy infrastructure on first run
fi

echo -e "${BLUE}Changes detected:${NC}"
echo "  Frontend: $FRONTEND_CHANGED files"
echo "  Backend: $BACKEND_CHANGED files"
echo "  Infrastructure: $INFRA_CHANGED files"
echo ""

# Determine what to deploy
DEPLOY_FRONTEND=false
DEPLOY_BACKEND=false
DEPLOY_INFRA=false

if [ $FRONTEND_CHANGED -gt 0 ] && [ "$AUTO_DEPLOY_FRONTEND" == "true" ]; then
    DEPLOY_FRONTEND=true
    echo -e "${GREEN}✓ Frontend will be deployed${NC}"
fi

if [ $BACKEND_CHANGED -gt 0 ] && [ "$AUTO_DEPLOY_BACKEND" == "true" ]; then
    DEPLOY_BACKEND=true
    echo -e "${GREEN}✓ Backend will be deployed${NC}"
fi

if [ $INFRA_CHANGED -gt 0 ] && [ "$AUTO_DEPLOY_INFRASTRUCTURE" == "true" ]; then
    DEPLOY_INFRA=true
    echo -e "${GREEN}✓ Infrastructure will be deployed${NC}"
fi

# Check if anything needs deployment
if [ "$DEPLOY_FRONTEND" == "false" ] && [ "$DEPLOY_BACKEND" == "false" ] && [ "$DEPLOY_INFRA" == "false" ]; then
    echo -e "${YELLOW}No changes require deployment${NC}"
    exit 0
fi

# Require confirmation if enabled
if [ "$REQUIRE_CONFIRMATION" == "true" ]; then
    echo ""
    read -p "Proceed with automatic deployment? (y/n): " CONFIRM
    if [ "$CONFIRM" != "y" ]; then
        echo -e "${RED}Deployment cancelled${NC}"
        exit 0
    fi
fi

echo ""
echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}   Starting Deployment${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""

DEPLOYMENT_START=$(date +%s)
DEPLOYED_SOMETHING=false

# Deploy infrastructure first (if needed)
if [ "$DEPLOY_INFRA" == "true" ]; then
    echo -e "${BLUE}▶ Deploying Infrastructure...${NC}"
    echo ""

    if "$SCRIPT_DIR/deploy-infrastructure.sh" apply; then
        echo -e "${GREEN}✅ Infrastructure deployed${NC}"
        DEPLOYED_SOMETHING=true
    else
        echo -e "${RED}❌ Infrastructure deployment failed${NC}"
        exit 1
    fi
    echo ""
fi

# Deploy backend
if [ "$DEPLOY_BACKEND" == "true" ]; then
    echo -e "${BLUE}▶ Deploying Backend...${NC}"
    echo ""

    if "$SCRIPT_DIR/deploy-backend.sh"; then
        echo -e "${GREEN}✅ Backend deployed${NC}"
        DEPLOYED_SOMETHING=true
    else
        echo -e "${RED}❌ Backend deployment failed${NC}"
        exit 1
    fi
    echo ""
fi

# Deploy frontend
if [ "$DEPLOY_FRONTEND" == "true" ]; then
    echo -e "${BLUE}▶ Deploying Frontend...${NC}"
    echo ""

    if "$SCRIPT_DIR/deploy-frontend.sh"; then
        echo -e "${GREEN}✅ Frontend deployed${NC}"
        DEPLOYED_SOMETHING=true
    else
        echo -e "${RED}❌ Frontend deployment failed${NC}"
        exit 1
    fi
    echo ""
fi

if [ "$DEPLOYED_SOMETHING" == "false" ]; then
    echo -e "${YELLOW}Nothing was deployed${NC}"
    exit 0
fi

# Save current commit as last deploy
echo "$CURRENT_COMMIT" > "$LAST_DEPLOY_FILE"

DEPLOYMENT_END=$(date +%s)
DEPLOYMENT_TIME=$((DEPLOYMENT_END - DEPLOYMENT_START))

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}   ✅ Deployment Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Deployment time: ${DEPLOYMENT_TIME}s"
echo "Deployed commit: $(git rev-parse --short HEAD)"
echo ""

# Show what was deployed
echo "Components deployed:"
[ "$DEPLOY_INFRA" == "true" ] && echo "  ✓ Infrastructure"
[ "$DEPLOY_BACKEND" == "true" ] && echo "  ✓ Backend"
[ "$DEPLOY_FRONTEND" == "true" ] && echo "  ✓ Frontend"
echo ""
