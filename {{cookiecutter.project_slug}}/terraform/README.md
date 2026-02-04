# StoryArchitect Infrastructure

This directory contains the complete Infrastructure as Code (IaC) for the StoryArchitect application using Terraform.

## Architecture Overview

### Frontend
- **S3 Bucket**: Static website hosting for React app
- **CloudFront**: CDN for global content delivery
- **Route53**: DNS management for custom domain

### Backend (On-Demand)
- **ECR**: Container registry for Docker images
- **ECS Fargate**: Serverless container execution
- **API Gateway**: HTTP API with `/start` endpoint
- **Lambda Functions**:
  - **Task Manager**: Starts new tasks or extends lifetime, publishes ping metrics
  - **Task Monitor**: Triggered by alarm when task goes inactive, stops idle tasks
- **CloudWatch Alarm**: Monitors TaskPing metric, triggers when no pings for 5 minutes
- **SNS**: Notification topic for alarm → Lambda trigger
- **DynamoDB**: Tracks task state and expiration time
- **S3**: Stores SQLite database with versioning

### How It Works

1. **Request Arrives**: User/app hits `https://storyarchitect.yerson.co/start`
2. **API Gateway**: Routes to Task Manager Lambda
3. **Task Manager Lambda**:
   - Checks if task is running
   - If no → Starts new ECS task, publishes initial ping metric
   - If yes → Extends lifetime by 5 minutes, publishes ping metric
4. **ECS Task Starts**:
   - Downloads SQLite DB from S3
   - Runs Django backend
5. **CloudWatch Alarm** (monitors TaskPing metric):
   - Evaluates every 5 minutes (configurable)
   - If no pings received → Goes into ALARM state
   - Publishes notification to SNS topic
6. **Task Monitor Lambda** (triggered by alarm):
   - Receives SNS notification from alarm
   - Stops the idle ECS task
7. **Task Shuts Down**:
   - Uploads SQLite DB back to S3
   - Task terminates
   - Alarm returns to OK state on next ping

## Directory Structure

```
terraform/
├── modules/
│   ├── s3/              # Frontend & database S3 buckets
│   ├── ecr/             # Container registry
│   ├── ecs/             # ECS cluster & task definition
│   ├── lambda/          # Lambda functions & EventBridge
│   ├── apigateway/      # HTTP API configuration
│   ├── cloudfront/      # CDN for frontend
│   └── route53/         # DNS records
├── lambda_functions/
│   ├── task_manager/    # Start/extend task lifecycle
│   └── task_monitor/    # Monitor and stop idle tasks
└── environments/
    └── prod/            # Production environment configuration
```

## Prerequisites

1. **AWS Account** with appropriate permissions
2. **Terraform** >= 1.0 installed
3. **AWS CLI** configured
4. **Domain name** (optional but recommended)
5. **ACM Certificates** (if using custom domain):
   - Frontend certificate in `us-east-1` (for CloudFront)
   - API certificate in your region (for API Gateway)

## Setup Instructions

### 1. Configure Variables

Copy the example variables file:

```bash
cd terraform/environments/prod
cp terraform.tfvars.example terraform.tfvars
```

Edit `terraform.tfvars` with your configuration:

```hcl
aws_region  = "us-east-1"
environment = "prod"

# S3 Buckets (must be globally unique)
frontend_bucket_name = "storyarchitect-frontend-prod"
database_bucket_name = "storyarchitect-database-prod"

# ECS Configuration
ecs_task_cpu           = "512"
ecs_task_memory        = "1024"
task_lifetime_seconds  = 300  # 5 minutes

# Optional: Custom Domain Configuration
# hosted_zone_name          = "yerson.co"
# frontend_subdomain        = "app.yerson.co"
# api_subdomain             = "storyarchitect.yerson.co"
# frontend_domain_aliases   = ["app.yerson.co"]
# api_domain_name           = "storyarchitect.yerson.co"
# frontend_certificate_arn  = "arn:aws:acm:..."
# api_certificate_arn       = "arn:aws:acm:..."
```

### 2. Initialize Terraform

```bash
cd terraform/environments/prod
terraform init
```

### 3. Review the Plan

```bash
terraform plan
```

### 4. Apply Infrastructure

```bash
terraform apply
```

This will create:
- 2 S3 buckets (frontend + database)
- 1 ECR repository
- 1 ECS cluster + task definition
- 2 Lambda functions
- 1 API Gateway
- 1 CloudFront distribution
- DynamoDB table for task state
- IAM roles and policies
- CloudWatch logs and EventBridge rules

### 5. Configure GitHub Secrets

After Terraform completes, configure these GitHub repository secrets:

```
AWS_ACCESS_KEY_ID=<your-access-key>
AWS_SECRET_ACCESS_KEY=<your-secret-key>
FRONTEND_S3_BUCKET=<output from terraform>
CLOUDFRONT_DISTRIBUTION_ID=<output from terraform>
ECS_CLUSTER_NAME=<output from terraform>
ECS_SERVICE_NAME=  # Leave empty for on-demand setup
```

Get the values from Terraform outputs:

```bash
terraform output
```

### 6. Configure Environment Variables

Create a `.env` file in project root with Terraform outputs:

```bash
cat > ../../.env <<EOF
export AWS_REGION=us-east-1
export FRONTEND_S3_BUCKET=$(terraform output -raw frontend_bucket_name)
export CLOUDFRONT_DISTRIBUTION_ID=$(terraform output -raw cloudfront_distribution_id)
export DATABASE_S3_BUCKET=$(terraform output -raw database_bucket_name)
export ECR_REPOSITORY=storyarchitect-backend
EOF

# Add to .gitignore
echo ".env" >> ../../.gitignore
```

### 7. Deploy Using Scripts

Use the deployment scripts in the `scripts/` directory:

```bash
cd ../../

# Load environment variables
source .env

# Deploy everything
./scripts/deploy.sh

# Or deploy individually:
./scripts/deploy-backend.sh   # Build and push Docker image to ECR
./scripts/deploy-frontend.sh  # Deploy React app to S3 + CloudFront
```

## Deployment Workflows

The project uses shell scripts for deployment with automatic change detection.

### Master Deployment Script

**Script**: `scripts/deploy.sh`

**Features**:
- Auto-detects changes since last deployment
- Deploys only what changed
- Interactive prompts for confirmation

**Usage**:
```bash
source .env
./scripts/deploy.sh
```

### Individual Component Scripts

**Frontend Deployment** (`scripts/deploy-frontend.sh`):
1. Installs npm dependencies
2. Builds React app
3. Syncs to S3 with optimized cache headers
4. Creates CloudFront invalidation

**Backend Deployment** (`scripts/deploy-backend.sh`):
1. Builds Docker image
2. Logs into ECR
3. Pushes image with commit SHA + `latest` tags
4. ECS tasks use new image on next start

**Infrastructure Deployment** (`scripts/deploy-infrastructure.sh`):
1. Runs terraform init
2. Validates configuration
3. Creates and applies plan

## Testing the Setup

### 1. Test Backend Start

```bash
curl https://storyarchitect.yerson.co/start
# or use the API Gateway URL if no custom domain
curl https://<api-id>.execute-api.us-east-1.amazonaws.com/prod/start
```

Expected response:
```json
{
  "status": "started",
  "task_arn": "arn:aws:ecs:...",
  "public_ip": "54.XXX.XXX.XXX",
  "message": "Task starting. Please wait 30-60 seconds for it to be ready."
}
```

### 2. Wait for Task to Start

Give it 30-60 seconds for the task to download the DB and start Django.

### 3. Test Backend API

```bash
curl http://<public-ip>:8000/health/
```

### 4. Extend Task Lifetime

```bash
curl https://storyarchitect.yerson.co/start?action=ping
```

### 5. Wait for Auto-Shutdown

After 5 minutes of no pings, the task will automatically shut down and save the DB to S3.

## Cost Optimization

### On-Demand Backend Costs

- **Lambda**: First 1M requests free, $0.20 per 1M after
- **API Gateway**: $1.00 per million requests
- **ECS Fargate**: $0.04048/hour for 0.5 vCPU, 1 GB
  - Running 5 min/hour = ~$0.003/hour
  - Running 1 hour/day = $0.04/day = $1.20/month
- **DynamoDB**: Pay-per-request (very cheap for this use case)
- **S3 Database Storage**: ~$0.023/GB/month
- **CloudWatch Logs**: ~$0.50/GB ingested

**Estimated monthly cost (light usage)**: $5-15/month

### Frontend Costs

- **S3**: $0.023/GB storage + $0.005/10k GET requests
- **CloudFront**: $0.085/GB for first 10 TB

## Maintenance

### Viewing Task Logs

```bash
aws logs tail /ecs/storyarchitect-prod --follow
```

### Manually Stopping a Task

```bash
aws ecs stop-task \
  --cluster storyarchitect-prod \
  --task <task-arn> \
  --reason "Manual shutdown"
```

### Checking Task State

```bash
aws dynamodb get-item \
  --table-name storyarchitect-task-state-prod \
  --key '{"task_id": {"S": "main"}}'
```

### Database Backups

The database bucket has versioning enabled. To list versions:

```bash
aws s3api list-object-versions \
  --bucket storyarchitect-database-prod \
  --prefix db.sqlite3
```

To restore a specific version:

```bash
aws s3api get-object \
  --bucket storyarchitect-database-prod \
  --key db.sqlite3 \
  --version-id <version-id> \
  db-restore.sqlite3
```

## Troubleshooting

### Task Won't Start

1. Check Lambda logs:
   ```bash
   aws logs tail /aws/lambda/storyarchitect-task-manager-prod --follow
   ```

2. Verify task definition exists:
   ```bash
   aws ecs describe-task-definition \
     --task-definition storyarchitect-backend-prod
   ```

3. Check subnet and security group configuration

### Task Starts but Backend Unreachable

1. Verify security group allows inbound port 8000
2. Check task logs for errors
3. Ensure health check endpoint `/health/` exists

### Database Not Syncing

1. Check task IAM role has S3 permissions
2. View container logs for sync errors
3. Verify `DB_S3_BUCKET` environment variable is set

### Frontend Not Updating

1. Verify CloudFront invalidation completed
2. Check S3 bucket contents
3. Clear browser cache

## Security Considerations

1. **Database Encryption**: Enable S3 encryption at rest
2. **API Authentication**: Add API Gateway authorizer (Lambda or Cognito)
3. **Network Isolation**: Use private subnets for ECS tasks (requires NAT Gateway)
4. **IAM Least Privilege**: Review and tighten IAM policies
5. **Secrets Management**: Use AWS Secrets Manager for sensitive data

## Cleanup

To destroy all infrastructure:

```bash
cd terraform/environments/prod
terraform destroy
```

**Note**: This will delete all resources including S3 buckets. Make sure to backup your database first!

## Support

For issues or questions:
- Check CloudWatch Logs
- Review Terraform plan before applying changes
- Consult AWS documentation for specific services

## License

MIT
