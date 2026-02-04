#!/bin/bash
# Frontend deployment script

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
AWS_REGION="${AWS_REGION:-us-east-1}"
FRONTEND_DIR="frontend"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}   Frontend Deployment Script${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if in correct directory
if [ ! -d "$FRONTEND_DIR" ]; then
    echo -e "${RED}Error: frontend/ directory not found${NC}"
    echo "Please run this script from the project root"
    exit 1
fi

# Check AWS credentials
if ! aws sts get-caller-identity &>/dev/null; then
    echo -e "${RED}Error: AWS credentials not configured${NC}"
    echo "Run: aws configure"
    exit 1
fi

# Get S3 bucket and CloudFront ID
if [ -z "$FRONTEND_S3_BUCKET" ]; then
    echo -e "${YELLOW}FRONTEND_S3_BUCKET not set in environment${NC}"
    read -p "Enter S3 bucket name: " FRONTEND_S3_BUCKET
fi

if [ -z "$CLOUDFRONT_DISTRIBUTION_ID" ]; then
    echo -e "${YELLOW}CLOUDFRONT_DISTRIBUTION_ID not set in environment${NC}"
    read -p "Enter CloudFront distribution ID (or press Enter to skip): " CLOUDFRONT_DISTRIBUTION_ID
fi

echo ""
echo -e "${GREEN}Configuration:${NC}"
echo "  AWS Region: $AWS_REGION"
echo "  S3 Bucket: $FRONTEND_S3_BUCKET"
echo "  CloudFront: ${CLOUDFRONT_DISTRIBUTION_ID:-N/A}"
echo ""

# Install dependencies
echo -e "${BLUE}📦 Installing dependencies...${NC}"
cd $FRONTEND_DIR
npm ci --prefer-offline --no-audit

# Build
echo -e "${BLUE}🔨 Building React application...${NC}"
GENERATE_SOURCEMAP=false CI=false npm run build

if [ ! -d "build" ]; then
    echo -e "${RED}Error: Build directory not found${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Build completed successfully${NC}"

# Deploy to S3
echo -e "${BLUE}☁️  Deploying to S3...${NC}"

# Sync static assets with long cache
aws s3 sync build/ s3://$FRONTEND_S3_BUCKET/ \
    --delete \
    --cache-control "public,max-age=31536000,immutable" \
    --exclude "index.html" \
    --exclude "asset-manifest.json" \
    --region $AWS_REGION

# Upload index.html with no-cache
aws s3 cp build/index.html s3://$FRONTEND_S3_BUCKET/index.html \
    --cache-control "public,max-age=0,must-revalidate" \
    --content-type "text/html" \
    --region $AWS_REGION

# Upload asset-manifest.json if exists
if [ -f "build/asset-manifest.json" ]; then
    aws s3 cp build/asset-manifest.json s3://$FRONTEND_S3_BUCKET/asset-manifest.json \
        --cache-control "public,max-age=0,must-revalidate" \
        --content-type "application/json" \
        --region $AWS_REGION
fi

echo -e "${GREEN}✅ S3 deployment completed${NC}"

# CloudFront invalidation
if [ -n "$CLOUDFRONT_DISTRIBUTION_ID" ]; then
    echo -e "${BLUE}🔄 Creating CloudFront invalidation...${NC}"

    INVALIDATION_ID=$(aws cloudfront create-invalidation \
        --distribution-id $CLOUDFRONT_DISTRIBUTION_ID \
        --paths "/*" \
        --query 'Invalidation.Id' \
        --output text)

    echo "Invalidation ID: $INVALIDATION_ID"
    echo -e "${YELLOW}Waiting for invalidation to complete (this may take 1-2 minutes)...${NC}"

    aws cloudfront wait invalidation-completed \
        --distribution-id $CLOUDFRONT_DISTRIBUTION_ID \
        --id $INVALIDATION_ID

    echo -e "${GREEN}✅ CloudFront invalidation completed${NC}"
else
    echo -e "${YELLOW}⚠️  Skipping CloudFront invalidation (no distribution ID)${NC}"
fi

# Summary
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}   ✅ Frontend Deployed Successfully!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "S3 Bucket: $FRONTEND_S3_BUCKET"
echo "CloudFront: ${CLOUDFRONT_DISTRIBUTION_ID:-N/A}"
echo ""
echo -e "${BLUE}🌐 Frontend URL:${NC}"
if [ -n "$CLOUDFRONT_DISTRIBUTION_ID" ]; then
    DOMAIN=$(aws cloudfront get-distribution --id $CLOUDFRONT_DISTRIBUTION_ID --query 'Distribution.DomainName' --output text 2>/dev/null || echo "")
    if [ -n "$DOMAIN" ]; then
        echo "   https://$DOMAIN"
    fi
fi
echo "   http://$FRONTEND_S3_BUCKET.s3-website-$AWS_REGION.amazonaws.com"
echo ""

cd ..
