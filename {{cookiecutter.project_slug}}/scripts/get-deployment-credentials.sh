#!/bin/bash
# Get deployment credentials from SSM Parameter Store

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
AWS_REGION="${AWS_REGION:-us-east-1}"
PROJECT_NAME="${PROJECT_NAME:-storyarchitect}"
ENVIRONMENT="${ENVIRONMENT:-prod}"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}   Deployment Credentials Retrieval${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check AWS credentials
if ! aws sts get-caller-identity &>/dev/null; then
    echo -e "${RED}Error: AWS credentials not configured${NC}"
    echo "Run: aws configure"
    exit 1
fi

echo -e "${GREEN}Configuration:${NC}"
echo "  AWS Region: $AWS_REGION"
echo "  Project: $PROJECT_NAME"
echo "  Environment: $ENVIRONMENT"
echo ""

# Parameter names
ACCESS_KEY_PARAM="/${PROJECT_NAME}/${ENVIRONMENT}/deployment/access-key-id"
SECRET_KEY_PARAM="/${PROJECT_NAME}/${ENVIRONMENT}/deployment/secret-access-key"

echo -e "${BLUE}Retrieving credentials from SSM Parameter Store...${NC}"
echo ""

# Get access key ID
echo -e "${YELLOW}Access Key ID:${NC}"
ACCESS_KEY_ID=$(aws ssm get-parameter \
    --name "$ACCESS_KEY_PARAM" \
    --region "$AWS_REGION" \
    --query 'Parameter.Value' \
    --output text 2>&1)

if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Could not retrieve access key ID${NC}"
    echo "Make sure the deployment user has been created with Terraform"
    echo ""
    echo "To create the deployment user:"
    echo "  1. Edit terraform/environments/prod/terraform.tfvars"
    echo "  2. Set: create_deployment_user = true"
    echo "  3. Run: make infra-apply"
    exit 1
fi

echo "$ACCESS_KEY_ID"
echo ""

# Get secret access key
echo -e "${YELLOW}Secret Access Key:${NC}"
SECRET_ACCESS_KEY=$(aws ssm get-parameter \
    --name "$SECRET_KEY_PARAM" \
    --region "$AWS_REGION" \
    --with-decryption \
    --query 'Parameter.Value' \
    --output text 2>&1)

if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Could not retrieve secret access key${NC}"
    exit 1
fi

echo "$SECRET_ACCESS_KEY"
echo ""

# Optionally configure AWS CLI profile
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}   Configuration Options${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo "Choose how to use these credentials:"
echo "  1) Configure AWS CLI profile (recommended)"
echo "  2) Export as environment variables (current session)"
echo "  3) Add to .env file"
echo "  4) Display only (already shown above)"
echo ""
read -p "Choice [1-4]: " CHOICE

case $CHOICE in
    1)
        PROFILE_NAME="${PROJECT_NAME}-deployment"
        echo ""
        echo -e "${BLUE}Configuring AWS CLI profile: $PROFILE_NAME${NC}"

        aws configure set aws_access_key_id "$ACCESS_KEY_ID" --profile "$PROFILE_NAME"
        aws configure set aws_secret_access_key "$SECRET_ACCESS_KEY" --profile "$PROFILE_NAME"
        aws configure set region "$AWS_REGION" --profile "$PROFILE_NAME"

        echo -e "${GREEN}✅ Profile configured: $PROFILE_NAME${NC}"
        echo ""
        echo "To use this profile:"
        echo "  export AWS_PROFILE=$PROFILE_NAME"
        echo ""
        echo "Or add to your .env file:"
        echo "  export AWS_PROFILE=$PROFILE_NAME"
        ;;
    2)
        echo ""
        echo -e "${YELLOW}Export these variables in your terminal:${NC}"
        echo ""
        echo "export AWS_ACCESS_KEY_ID='$ACCESS_KEY_ID'"
        echo "export AWS_SECRET_ACCESS_KEY='$SECRET_ACCESS_KEY'"
        echo "export AWS_REGION='$AWS_REGION'"
        echo ""
        echo -e "${BLUE}Or run:${NC}"
        echo "eval \"\$(./scripts/get-deployment-credentials.sh)\""
        ;;
    3)
        ENV_FILE=".env"
        if [ -f "$ENV_FILE" ]; then
            echo ""
            echo -e "${YELLOW}⚠️  .env file already exists${NC}"
            read -p "Append to existing file? (y/n): " APPEND
            if [ "$APPEND" != "y" ]; then
                echo -e "${RED}Aborted${NC}"
                exit 0
            fi
        fi

        echo "" >> "$ENV_FILE"
        echo "# Deployment credentials (generated $(date))" >> "$ENV_FILE"
        echo "export AWS_ACCESS_KEY_ID='$ACCESS_KEY_ID'" >> "$ENV_FILE"
        echo "export AWS_SECRET_ACCESS_KEY='$SECRET_ACCESS_KEY'" >> "$ENV_FILE"
        echo "export AWS_REGION='$AWS_REGION'" >> "$ENV_FILE"

        echo -e "${GREEN}✅ Credentials added to $ENV_FILE${NC}"
        echo ""
        echo "Load them with:"
        echo "  source .env"
        ;;
    4)
        echo ""
        echo -e "${GREEN}Credentials displayed above.${NC}"
        ;;
    *)
        echo -e "${RED}Invalid choice${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}   Done!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
