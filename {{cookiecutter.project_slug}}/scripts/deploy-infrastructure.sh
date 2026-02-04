#!/bin/bash
# Infrastructure deployment script - Terraform apply

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
AWS_REGION="${AWS_REGION:-us-east-1}"
TF_DIR="terraform/environments/prod"
TF_ACTION="${1:-plan}"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}   Infrastructure Deployment Script${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if in correct directory
if [ ! -d "$TF_DIR" ]; then
    echo -e "${RED}Error: $TF_DIR directory not found${NC}"
    echo "Please run this script from the project root"
    exit 1
fi

# Check Terraform installed
if ! command -v terraform &>/dev/null; then
    echo -e "${RED}Error: Terraform not installed${NC}"
    echo "Install: https://www.terraform.io/downloads"
    exit 1
fi

# Check AWS credentials
if ! aws sts get-caller-identity &>/dev/null; then
    echo -e "${RED}Error: AWS credentials not configured${NC}"
    echo "Run: aws configure"
    exit 1
fi

echo -e "${GREEN}Configuration:${NC}"
echo "  Terraform Directory: $TF_DIR"
echo "  Action: $TF_ACTION"
echo "  AWS Region: $AWS_REGION"
echo ""

cd $TF_DIR

# Check for terraform.tfvars
if [ ! -f "terraform.tfvars" ]; then
    echo -e "${YELLOW}⚠️  terraform.tfvars not found${NC}"
    echo ""
    echo "Creating terraform.tfvars from environment variables..."
    echo ""

    cat > terraform.tfvars <<EOF
# Terraform configuration
aws_region   = "$AWS_REGION"
environment  = "prod"
project_name = "storyarchitect"

# S3 Buckets (must be globally unique!)
frontend_bucket_name = "${FRONTEND_S3_BUCKET:-storyarchitect-frontend-prod}"
database_bucket_name = "${DATABASE_S3_BUCKET:-storyarchitect-database-prod}"

# ECR
ecr_repository_name = "storyarchitect-backend"

# ECS Configuration
ecs_task_cpu          = "512"
ecs_task_memory       = "1024"
task_lifetime_seconds = 300

# Domain Configuration (optional)
# hosted_zone_name        = "yerson.co"
# frontend_subdomain      = "app.yerson.co"
# api_subdomain           = "storyarchitect.yerson.co"
# frontend_domain_aliases = ["app.yerson.co"]
# api_domain_name         = "storyarchitect.yerson.co"

# SSL Certificates (optional)
# frontend_certificate_arn = "arn:aws:acm:us-east-1:..."
# api_certificate_arn      = "arn:aws:acm:us-east-1:..."
EOF

    echo -e "${GREEN}✅ Created terraform.tfvars${NC}"
    echo -e "${YELLOW}📝 Please edit terraform/environments/prod/terraform.tfvars with your configuration${NC}"
    echo ""
    read -p "Press Enter to continue or Ctrl+C to exit and edit the file..."
fi

# Initialize Terraform
echo -e "${BLUE}🔧 Initializing Terraform...${NC}"
terraform init -input=false

# Validate
echo -e "${BLUE}✅ Validating Terraform configuration...${NC}"
terraform validate

# Format check
echo -e "${BLUE}📝 Checking Terraform formatting...${NC}"
terraform fmt -check -recursive || {
    echo -e "${YELLOW}⚠️  Formatting issues found. Run: terraform fmt -recursive${NC}"
}

# Plan
echo -e "${BLUE}📋 Creating Terraform plan...${NC}"
terraform plan -input=false -out=tfplan

echo ""
echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}   Terraform Plan Created${NC}"
echo -e "${YELLOW}========================================${NC}"
echo ""

if [ "$TF_ACTION" == "plan" ]; then
    echo -e "${GREEN}✅ Plan complete. Review above.${NC}"
    echo ""
    echo "To apply:"
    echo "  ./scripts/deploy-infrastructure.sh apply"
    echo ""
    exit 0
fi

if [ "$TF_ACTION" == "apply" ]; then
    echo -e "${YELLOW}⚠️  About to apply Terraform changes!${NC}"
    echo ""
    read -p "Are you sure? (yes/no): " CONFIRM

    if [ "$CONFIRM" != "yes" ]; then
        echo -e "${RED}Aborted.${NC}"
        exit 1
    fi

    echo -e "${BLUE}🚀 Applying Terraform changes...${NC}"
    terraform apply -auto-approve -input=false tfplan

    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}   ✅ Infrastructure Deployed!${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""

    # Show outputs
    echo -e "${BLUE}📊 Infrastructure Outputs:${NC}"
    echo ""
    terraform output

    echo ""
    echo -e "${BLUE}📝 Save these values:${NC}"
    echo "  FRONTEND_S3_BUCKET=$(terraform output -raw frontend_bucket_name 2>/dev/null || echo 'N/A')"
    echo "  CLOUDFRONT_DISTRIBUTION_ID=$(terraform output -raw cloudfront_distribution_id 2>/dev/null || echo 'N/A')"
    echo "  ECR_REPOSITORY=$(terraform output -raw ecr_repository_url 2>/dev/null || echo 'N/A')"
    echo "  API_ENDPOINT=$(terraform output -raw api_start_endpoint 2>/dev/null || echo 'N/A')"
    echo ""

elif [ "$TF_ACTION" == "destroy" ]; then
    echo -e "${RED}========================================${NC}"
    echo -e "${RED}   ⚠️  DESTROY INFRASTRUCTURE ⚠️${NC}"
    echo -e "${RED}========================================${NC}"
    echo ""
    echo -e "${RED}This will DELETE ALL resources!${NC}"
    echo ""
    read -p "Type 'destroy' to confirm: " CONFIRM

    if [ "$CONFIRM" != "destroy" ]; then
        echo -e "${RED}Aborted.${NC}"
        exit 1
    fi

    echo -e "${RED}🔥 Destroying infrastructure...${NC}"
    terraform destroy -auto-approve -input=false

    echo ""
    echo -e "${YELLOW}⚠️  All infrastructure has been destroyed${NC}"
    echo ""

else
    echo -e "${RED}Invalid action: $TF_ACTION${NC}"
    echo "Usage: $0 [plan|apply|destroy]"
    exit 1
fi

cd - > /dev/null
