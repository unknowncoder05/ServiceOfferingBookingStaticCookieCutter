#!/bin/bash
# Master deployment script - Detects changes and deploys accordingly

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

echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}   StoryArchitect Deployment${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""

# Change to project root
cd "$PROJECT_ROOT"

# Detect changes since last deployment
LAST_DEPLOY_COMMIT=$(cat .last-deploy 2>/dev/null || echo "")

if [ -z "$LAST_DEPLOY_COMMIT" ]; then
    echo -e "${YELLOW}No previous deployment found${NC}"
    echo -e "${YELLOW}This will deploy all components${NC}"
    echo ""

    # Ask what to deploy
    echo "What would you like to deploy?"
    echo "  1) All (Infrastructure + Backend + Frontend)"
    echo "  2) Infrastructure only"
    echo "  3) Backend only"
    echo "  4) Frontend only"
    echo "  5) Custom selection"
    read -p "Choice [1-5]: " CHOICE

    case $CHOICE in
        1)
            DEPLOY_INFRA=true
            DEPLOY_BACKEND=true
            DEPLOY_FRONTEND=true
            ;;
        2)
            DEPLOY_INFRA=true
            DEPLOY_BACKEND=false
            DEPLOY_FRONTEND=false
            ;;
        3)
            DEPLOY_INFRA=false
            DEPLOY_BACKEND=true
            DEPLOY_FRONTEND=false
            ;;
        4)
            DEPLOY_INFRA=false
            DEPLOY_BACKEND=false
            DEPLOY_FRONTEND=true
            ;;
        5)
            read -p "Deploy Infrastructure? (y/n): " DEPLOY_INFRA
            read -p "Deploy Backend? (y/n): " DEPLOY_BACKEND
            read -p "Deploy Frontend? (y/n): " DEPLOY_FRONTEND
            [ "$DEPLOY_INFRA" == "y" ] && DEPLOY_INFRA=true || DEPLOY_INFRA=false
            [ "$DEPLOY_BACKEND" == "y" ] && DEPLOY_BACKEND=true || DEPLOY_BACKEND=false
            [ "$DEPLOY_FRONTEND" == "y" ] && DEPLOY_FRONTEND=true || DEPLOY_FRONTEND=false
            ;;
        *)
            echo -e "${RED}Invalid choice${NC}"
            exit 1
            ;;
    esac
else
    # Auto-detect changes
    echo -e "${BLUE}Detecting changes since last deployment...${NC}"
    echo "Last deploy: $LAST_DEPLOY_COMMIT"
    echo "Current commit: $(git rev-parse --short HEAD)"
    echo ""

    FRONTEND_CHANGED=$(git diff --name-only $LAST_DEPLOY_COMMIT HEAD | grep -c "^frontend/" || true)
    BACKEND_CHANGED=$(git diff --name-only $LAST_DEPLOY_COMMIT HEAD | grep -c "^BackEndApi/" || true)
    INFRA_CHANGED=$(git diff --name-only $LAST_DEPLOY_COMMIT HEAD | grep -c "^terraform/" || true)

    echo "Changes detected:"
    echo "  Frontend: $FRONTEND_CHANGED files"
    echo "  Backend: $BACKEND_CHANGED files"
    echo "  Infrastructure: $INFRA_CHANGED files"
    echo ""

    DEPLOY_FRONTEND=false
    DEPLOY_BACKEND=false
    DEPLOY_INFRA=false

    if [ $FRONTEND_CHANGED -gt 0 ]; then
        DEPLOY_FRONTEND=true
        echo -e "${GREEN}✓ Frontend will be deployed${NC}"
    fi

    if [ $BACKEND_CHANGED -gt 0 ]; then
        DEPLOY_BACKEND=true
        echo -e "${GREEN}✓ Backend will be deployed${NC}"
    fi

    if [ $INFRA_CHANGED -gt 0 ]; then
        DEPLOY_INFRA=true
        echo -e "${GREEN}✓ Infrastructure will be deployed${NC}"
    fi

    if [ "$DEPLOY_FRONTEND" == "false" ] && [ "$DEPLOY_BACKEND" == "false" ] && [ "$DEPLOY_INFRA" == "false" ]; then
        echo -e "${YELLOW}No changes detected. Nothing to deploy.${NC}"
        read -p "Deploy anyway? (y/n): " FORCE
        if [ "$FORCE" == "y" ]; then
            read -p "Deploy what? (frontend/backend/infrastructure/all): " COMPONENT
            case $COMPONENT in
                frontend)
                    DEPLOY_FRONTEND=true
                    ;;
                backend)
                    DEPLOY_BACKEND=true
                    ;;
                infrastructure)
                    DEPLOY_INFRA=true
                    ;;
                all)
                    DEPLOY_FRONTEND=true
                    DEPLOY_BACKEND=true
                    DEPLOY_INFRA=true
                    ;;
                *)
                    echo -e "${RED}Invalid component${NC}"
                    exit 1
                    ;;
            esac
        else
            exit 0
        fi
    fi

    echo ""
    read -p "Proceed with deployment? (y/n): " CONFIRM
    if [ "$CONFIRM" != "y" ]; then
        echo -e "${RED}Deployment cancelled${NC}"
        exit 1
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

    if $SCRIPT_DIR/deploy-infrastructure.sh apply; then
        echo -e "${GREEN}✅ Infrastructure deployed successfully${NC}"
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

    if $SCRIPT_DIR/deploy-backend.sh; then
        echo -e "${GREEN}✅ Backend deployed successfully${NC}"
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

    if $SCRIPT_DIR/deploy-frontend.sh; then
        echo -e "${GREEN}✅ Frontend deployed successfully${NC}"
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
git rev-parse HEAD > .last-deploy

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

echo -e "${BLUE}📝 Next steps:${NC}"
if [ "$DEPLOY_BACKEND" == "true" ]; then
    echo "  • Test backend: curl https://storyarchitect.yerson.co/start"
fi
if [ "$DEPLOY_FRONTEND" == "true" ]; then
    echo "  • Test frontend: Open your browser to the CloudFront URL"
fi
echo ""
