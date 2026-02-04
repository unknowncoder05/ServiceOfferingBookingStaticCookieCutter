#!/bin/bash
# Backend deployment script - Build and push Docker image to ECR

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
AWS_REGION="${AWS_REGION:-us-east-1}"
ECR_REPOSITORY="${ECR_REPOSITORY:-storyarchitect-backend}"
BACKEND_DIR="BackEndApi"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}   Backend Deployment Script${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if in correct directory
if [ ! -d "$BACKEND_DIR" ]; then
    echo -e "${RED}Error: BackEndApi/ directory not found${NC}"
    echo "Please run this script from the project root"
    exit 1
fi

# Check AWS credentials
if ! aws sts get-caller-identity &>/dev/null; then
    echo -e "${RED}Error: AWS credentials not configured${NC}"
    echo "Run: aws configure"
    exit 1
fi

# Get account ID
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_URI="$ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY"

# Generate image tag
IMAGE_TAG=$(git rev-parse --short=7 HEAD 2>/dev/null || echo "latest")

echo -e "${GREEN}Configuration:${NC}"
echo "  AWS Region: $AWS_REGION"
echo "  AWS Account: $ACCOUNT_ID"
echo "  ECR Repository: $ECR_REPOSITORY"
echo "  ECR URI: $ECR_URI"
echo "  Image Tag: $IMAGE_TAG"
echo ""

# Check if ECR repository exists
echo -e "${BLUE}🔍 Checking ECR repository...${NC}"
if ! aws ecr describe-repositories --repository-names $ECR_REPOSITORY --region $AWS_REGION &>/dev/null; then
    echo -e "${YELLOW}ECR repository not found. Creating...${NC}"
    aws ecr create-repository \
        --repository-name $ECR_REPOSITORY \
        --region $AWS_REGION \
        --image-scanning-configuration scanOnPush=true
    echo -e "${GREEN}✅ ECR repository created${NC}"
else
    echo -e "${GREEN}✅ ECR repository found${NC}"
fi

# Login to ECR
echo -e "${BLUE}🔐 Logging in to Amazon ECR...${NC}"
aws ecr get-login-password --region $AWS_REGION | \
    docker login --username AWS --password-stdin $ECR_URI

# Build Docker image
echo -e "${BLUE}🔨 Building Docker image...${NC}"
cd $BACKEND_DIR

docker build \
    -f compose/production/django/Dockerfile \
    -t $ECR_URI:$IMAGE_TAG \
    -t $ECR_URI:latest \
    --progress=plain \
    .

echo -e "${GREEN}✅ Docker image built successfully${NC}"

# Push to ECR
echo -e "${BLUE}☁️  Pushing image to ECR...${NC}"

docker push $ECR_URI:$IMAGE_TAG
docker push $ECR_URI:latest

echo -e "${GREEN}✅ Image pushed to ECR${NC}"

# Verify image
echo -e "${BLUE}🔍 Verifying image in ECR...${NC}"
IMAGE_SIZE=$(aws ecr describe-images \
    --repository-name $ECR_REPOSITORY \
    --image-ids imageTag=$IMAGE_TAG \
    --region $AWS_REGION \
    --query 'imageDetails[0].imageSizeInBytes' \
    --output text 2>/dev/null || echo "0")

if [ "$IMAGE_SIZE" != "0" ]; then
    IMAGE_SIZE_MB=$((IMAGE_SIZE / 1024 / 1024))
    echo -e "${GREEN}✅ Image verified: ${IMAGE_SIZE_MB}MB${NC}"
else
    echo -e "${YELLOW}⚠️  Could not verify image size${NC}"
fi

# Summary
cd ..
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}   ✅ Backend Deployed Successfully!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "ECR Repository: $ECR_URI"
echo "Image Tags: $IMAGE_TAG, latest"
echo ""
echo -e "${BLUE}📝 Next Steps:${NC}"
echo "  1. Backend runs on-demand via Lambda/API Gateway"
echo "  2. Test: curl https://storyarchitect.yerson.co/start"
echo "  3. New ECS tasks will automatically use this image"
echo ""
echo -e "${YELLOW}Note: No ECS service update needed for on-demand architecture${NC}"
echo ""
