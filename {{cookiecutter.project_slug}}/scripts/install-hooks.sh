#!/bin/bash
# Install git hooks and configure automatic deployment

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
HOOKS_DIR="$PROJECT_ROOT/.git/hooks"

echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}   StoryArchitect Deployment Setup${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""
echo "This will configure automatic deployment on push."
echo ""

# Ask user about auto-deploy preference
echo -e "${BLUE}Deployment options:${NC}"
echo "  1) Fully automatic - deploys on every push to main (recommended)"
echo "  2) Ask for confirmation before deploying"
echo "  3) Manual only - just install reminders"
echo ""
read -p "Choose deployment mode [1-3] (default: 1): " MODE
MODE=${MODE:-1}

# Create or update .deploy-config
CONFIG_FILE="$PROJECT_ROOT/.deploy-config"

case $MODE in
    1)
        cat > "$CONFIG_FILE" <<EOF
# StoryArchitect Auto-Deploy Configuration
AUTO_DEPLOY_ENABLED=true
AUTO_DEPLOY_FRONTEND=true
AUTO_DEPLOY_BACKEND=true
AUTO_DEPLOY_INFRASTRUCTURE=false
REQUIRE_CONFIRMATION=false
DEPLOY_BRANCH="main"
VERBOSE=true
EOF
        echo -e "${GREEN}✓ Configured for fully automatic deployment${NC}"
        ;;
    2)
        cat > "$CONFIG_FILE" <<EOF
# StoryArchitect Auto-Deploy Configuration
AUTO_DEPLOY_ENABLED=true
AUTO_DEPLOY_FRONTEND=true
AUTO_DEPLOY_BACKEND=true
AUTO_DEPLOY_INFRASTRUCTURE=false
REQUIRE_CONFIRMATION=true
DEPLOY_BRANCH="main"
VERBOSE=true
EOF
        echo -e "${GREEN}✓ Configured for deployment with confirmation${NC}"
        ;;
    3)
        cat > "$CONFIG_FILE" <<EOF
# StoryArchitect Auto-Deploy Configuration
AUTO_DEPLOY_ENABLED=false
AUTO_DEPLOY_FRONTEND=true
AUTO_DEPLOY_BACKEND=true
AUTO_DEPLOY_INFRASTRUCTURE=false
REQUIRE_CONFIRMATION=false
DEPLOY_BRANCH="main"
VERBOSE=true
EOF
        echo -e "${GREEN}✓ Configured for manual deployment only${NC}"
        ;;
esac

echo ""
echo -e "${BLUE}Setting up git configuration...${NC}"
echo ""

# Configure git aliases
git config alias.deploy-push '!bash scripts/git-push-deploy.sh'
echo "✅ Created git alias: git deploy-push"

# Option to make 'git push' automatically deploy
echo ""
read -p "Make 'git push' automatically deploy? (y/n) (default: y): " AUTO_PUSH
AUTO_PUSH=${AUTO_PUSH:-y}

if [ "$AUTO_PUSH" == "y" ]; then
    # Create a wrapper that intercepts git push
    git config alias.push-original '!git push'
    git config alias.push '!bash scripts/git-push-deploy.sh'
    echo "✅ Configured 'git push' to auto-deploy"
    echo -e "${YELLOW}   Note: Use 'git push-original' for push without deployment${NC}"
else
    echo "✅ 'git push' remains standard - use 'git deploy-push' to deploy"
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}   Setup Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${BLUE}Configuration saved to: .deploy-config${NC}"
echo ""
echo "How to use:"
if [ "$AUTO_PUSH" == "y" ]; then
    echo "  • git push               → Pushes and auto-deploys (NEW!)"
    echo "  • git push-original      → Push without deployment"
else
    echo "  • git push               → Standard push (no deployment)"
    echo "  • git deploy-push        → Push and auto-deploy"
fi
echo "  • ./scripts/deploy.sh    → Manual deployment"
echo ""
echo "You can change settings anytime by editing: .deploy-config"
echo ""
