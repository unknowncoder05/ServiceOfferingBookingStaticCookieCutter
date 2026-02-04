# {{ cookiecutter.project_name }} Infrastructure & Deployment Guide

## Quick Start

This project uses **Terraform** for infrastructure and **Git-based deployment scripts** with automatic change detection.

### Deployment Scripts

All deployment is managed through shell scripts in the `scripts/` directory:

1. **`deploy.sh`** - Master script that auto-detects changes and deploys accordingly
2. **`deploy-frontend.sh`** - Deploys React app to S3 + CloudFront
3. **`deploy-backend.sh`** - Builds Docker image and pushes to ECR
4. **`deploy-infrastructure.sh`** - Applies Terraform changes
5. **`install-hooks.sh`** - Installs git hooks for deployment reminders

### What Gets Deployed

1. **Frontend Changes** (`frontend/*`):
   - Builds React app
   - Deploys to S3
   - Invalidates CloudFront cache
   - Available at your custom domain

2. **Backend Changes** (`BackEndApi/*`):
   - Builds Docker image
   - Pushes to ECR
   - Backend runs on-demand when requested

3. **Infrastructure Changes** (`terraform/*`):
   - Plans and applies Terraform changes
   - Updates AWS resources

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         User/Browser                             │
└──────────────┬────────────────────────────────┬─────────────────┘
               │                                │
               │ Frontend                       │ Backend API
               ▼                                ▼
         ┌──────────┐                    ┌─────────────┐
         │CloudFront│                    │API Gateway  │
         │   CDN    │                    │   /start    │
         └────┬─────┘                    └──────┬──────┘
              │                                 │
              ▼                                 ▼
         ┌─────────┐                    ┌──────────────┐
         │   S3    │                    │   Lambda     │
         │Frontend │                    │Task Manager  │
         │ Bucket  │                    └──────┬───────┘
         └─────────┘                           │
                                               │ Starts/Extends
                                               ▼
                                        ┌──────────────┐
                                        │  ECS Fargate │
                                        │    Task      │
                                        └──────┬───────┘
                                               │
                      ┌────────────────────────┼─────────────────┐
                      │                        │                 │
                      ▼                        ▼                 ▼
                ┌─────────┐              ┌─────────┐      ┌──────────┐
                │   ECR   │              │   S3    │      │DynamoDB  │
                │ Images  │              │Database │      │Task State│
                └─────────┘              └─────────┘      └──────────┘
                                               ▲
                                               │ Stops when alarm triggers
                                         ┌─────┴──────┐
                                         │   Lambda   │
                                         │Task Monitor│
                                         └─────┬──────┘
                                               ▲
                                               │ SNS notification
                                         ┌─────┴──────────┐
                                         │  CloudWatch    │
                                         │     Alarm      │
                                         │ (TaskPing < 1) │
                                         └────────────────┘
                                               ▲
                                               │ Monitors metric
                                         ┌─────┴──────────┐
                                         │  CloudWatch    │
                                         │    Metrics     │
                                         │   (TaskPing)   │
                                         └────────────────┘
```

## On-Demand Backend Flow

1. **Cold Start** (No Task Running):
   ```
   Request → API Gateway → Lambda → Starts ECS Task
                                     ↓
                              Downloads DB from S3
                                     ↓
                              Runs Django Backend
                                     ↓
                              Returns Task Info
   ```

2. **Warm** (Task Already Running):
   ```
   Request → API Gateway → Lambda → Extends Lifetime
                                     (adds 5 more minutes)
   ```

3. **Automatic Shutdown**:
   ```
   No pings for 5 min → CloudWatch Alarm (ALARM state)
                                     ↓
                              SNS Topic publishes
                                     ↓
                         Task Monitor Lambda triggered
                                     ↓
                              Stops ECS Task
                                     ↓
                              Uploads DB to S3
   ```

## Setup Instructions

### Step 1: Configure AWS Credentials

You'll need two sets of AWS credentials:

#### 1. Admin/Terraform Credentials (For Infrastructure Deployment)

These are used to deploy the Terraform infrastructure (one-time setup or updates).

Create an IAM user with these managed policies:
- `AmazonEC2ContainerRegistryFullAccess`
- `AmazonECS_FullAccess`
- `AmazonS3FullAccess`
- `CloudFrontFullAccess`
- `AWSLambda_FullAccess`
- `AmazonDynamoDBFullAccess`
- `AmazonAPIGatewayAdministrator`
- `IAMFullAccess` (required to create deployment user)
- `AWSCertificateManagerFullAccess`
- `AmazonRoute53FullAccess`

Or use this Terraform-friendly policy:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:*",
        "cloudfront:*",
        "route53:*",
        "ecr:*",
        "ecs:*",
        "lambda:*",
        "apigateway:*",
        "dynamodb:*",
        "iam:*",
        "logs:*",
        "events:*",
        "ec2:DescribeNetworkInterfaces",
        "ec2:DescribeSubnets",
        "ec2:DescribeVpcs",
        "ec2:DescribeSecurityGroups"
      ],
      "Resource": "*"
    }
  ]
}
```

Configure these admin credentials:
```bash
aws configure
# Enter your admin access key, secret key, and region
```

#### 2. Deployment Credentials (Automatically Created)

Terraform will automatically create a scoped IAM user for deployments with minimal permissions:

**Permissions:**
- S3: Upload/delete frontend files, read database backups
- CloudFront: Create invalidations
- ECR: Push Docker images
- CloudWatch Logs: Read-only (for debugging)
- ECS: Read-only task status

**Security:**
- Stored in SSM Parameter Store (encrypted)
- No infrastructure modification permissions
- Scoped to specific resources only

The deployment user will be created when you run `terraform apply`. Credentials are retrieved using:
```bash
./scripts/get-deployment-credentials.sh
```

This script will:
1. Fetch credentials from SSM Parameter Store
2. Configure AWS CLI profile (`ProjectMaker}-deployment`)
3. Or export as environment variables
4. Or add to `.env` file

### Step 2: Create ACM Certificates (Optional)

If using a custom domain, create SSL certificates:

1. **Frontend Certificate** (for CloudFront):
   - **Must be in us-east-1 region**
   - Domain: `app.yerson.co` (or your subdomain)
   - Validation: DNS (Route53)

2. **API Certificate** (for API Gateway):
   - Can be in any region
   - Domain: `ProjectMaker}.yerson.co` (or your subdomain)
   - Validation: DNS (Route53)

```bash
# Create frontend cert (us-east-1)
aws acm request-certificate \
  --domain-name app.yerson.co \
  --validation-method DNS \
  --region us-east-1

# Create API cert (your region)
aws acm request-certificate \
  --domain-name ProjectMaker}.yerson.co \
  --validation-method DNS \
  --region us-east-1
```

Note the certificate ARNs for later use.

### Step 3: Configure Terraform

```bash
cd terraform/environments/prod
cp terraform.tfvars.example terraform.tfvars
```

Edit `terraform.tfvars`:

```hcl
# Basic Configuration
aws_region  = "us-east-1"
environment = "prod"

# S3 Buckets (must be globally unique!)
frontend_bucket_name = "ProjectMaker}-frontend-prod-yourname"
database_bucket_name = "ProjectMaker}-database-prod-yourname"

# ECS Configuration
ecs_task_cpu          = "512"   # 0.5 vCPU
ecs_task_memory       = "1024"  # 1 GB RAM
task_lifetime_seconds = 300     # 5 minutes

# Domain Configuration (Optional)
hosted_zone_name        = "yerson.co"
frontend_subdomain      = "app.yerson.co"
api_subdomain           = "ProjectMaker}.yerson.co"
frontend_domain_aliases = ["app.yerson.co"]
api_domain_name         = "ProjectMaker}.yerson.co"

# SSL Certificates (from Step 2)
frontend_certificate_arn = "arn:aws:acm:us-east-1:ACCOUNT:certificate/CERT_ID"
api_certificate_arn      = "arn:aws:acm:us-east-1:ACCOUNT:certificate/CERT_ID"
```

### Step 4: Deploy Infrastructure

```bash
cd terraform/environments/prod

# Initialize
terraform init

# Review plan
terraform plan

# Deploy
terraform apply
```

**Important**: Save the outputs! You'll need them for deployment scripts.

### Step 5: Get Deployment Credentials

Retrieve the automatically-created deployment user credentials:

```bash
cd ../../../  # Back to project root
./scripts/get-deployment-credentials.sh
```

This script will:
1. Fetch credentials from SSM Parameter Store
2. Offer to configure an AWS CLI profile
3. Or export as environment variables
4. Or add to `.env` file

**Recommended:** Choose option 1 to create an AWS CLI profile named `ProjectMaker}-deployment`.

### Step 6: Configure Environment Variables

Create a `.env` file in the project root with Terraform outputs:

```bash
cat > .env <<EOF
# AWS Configuration
export AWS_REGION=us-east-1
export AWS_PROFILE=ProjectMaker}-deployment  # Use deployment user profile

# S3 & CloudFront (from Terraform outputs)
export FRONTEND_S3_BUCKET=$(cd terraform/environments/prod && terraform output -raw frontend_bucket_name)
export CLOUDFRONT_DISTRIBUTION_ID=$(cd terraform/environments/prod && terraform output -raw cloudfront_distribution_id)
export DATABASE_S3_BUCKET=$(cd terraform/environments/prod && terraform output -raw database_bucket_name)

# ECR
export ECR_REPOSITORY=ProjectMaker}-backend
EOF

# Add .env to .gitignore (already done if following guide)
echo ".env" >> .gitignore
```

Load environment variables before deploying:
```bash
source .env
```

### Step 7: Install Git Hooks (Optional)

Install git hooks that remind you to deploy after pushing:

```bash
./scripts/install-hooks.sh
```

This creates hooks that prompt you to run `./scripts/deploy.sh` after committing to main.

### Step 8: Deploy Your Application

Use the master deployment script that auto-detects changes:

```bash
# Load environment variables
source .env

# Deploy everything (first time)
./scripts/deploy.sh
```

The script will:
1. Detect what changed (or ask what to deploy on first run)
2. Deploy infrastructure (if terraform/ changed)
3. Build and push backend Docker image (if BackEndApi/ changed)
4. Build and deploy frontend to S3 + CloudFront (if frontend/ changed)

Or deploy specific components:

```bash
# Deploy frontend only
./scripts/deploy-frontend.sh

# Deploy backend only
./scripts/deploy-backend.sh

# Deploy infrastructure only
./scripts/deploy-infrastructure.sh apply
```

### Step 9: Test the Setup

#### Test API Gateway

```bash
# Start backend task
curl https://ProjectMaker}.yerson.co/start

# Response:
{
  "status": "started",
  "task_arn": "arn:aws:ecs:...",
  "public_ip": "54.XXX.XXX.XXX",
  "message": "Task starting. Please wait 30-60 seconds for it to be ready."
}
```

#### Wait 60 seconds, then test backend

```bash
# Get public IP from previous response
curl http://<public-ip>:8000/api/story/projects/
```

#### Test auto-extend

```bash
curl https://ProjectMaker}.yerson.co/start?action=ping
```

#### Test frontend

Open browser to `https://app.yerson.co` (or your CloudFront URL)

## Deployment Workflow

### Automatic Change Detection

The `deploy.sh` script automatically detects what changed since the last deployment:

1. **Tracks deployment history**: Stores commit hash in `.last-deploy`
2. **Compares changes**: Uses `git diff` to find modified files
3. **Deploys only what changed**:
   - `frontend/` → Runs `deploy-frontend.sh`
   - `BackEndApi/` → Runs `deploy-backend.sh`
   - `terraform/` → Runs `deploy-infrastructure.sh`

### Making Changes

```bash
# 1. Make changes to your code
vim frontend/src/App.tsx

# 2. Commit changes
git add .
git commit -m "feat: update homepage"

# 3. Push to main
git push origin main

# 4. Deploy (auto-detects frontend changed)
source .env
./scripts/deploy.sh
```

The script will analyze changes and prompt you:
```
Changes detected:
  Frontend: 3 files
  Backend: 0 files
  Infrastructure: 0 files

✓ Frontend will be deployed

Proceed with deployment? (y/n):
```

### Deploying Specific Components

```bash
# Load environment variables
source .env

# Deploy frontend only
./scripts/deploy-frontend.sh

# Deploy backend only
./scripts/deploy-backend.sh

# Deploy infrastructure (plan first!)
./scripts/deploy-infrastructure.sh plan
./scripts/deploy-infrastructure.sh apply
```

### Git Hooks

If you installed git hooks with `./scripts/install-hooks.sh`, you'll see reminders:

**After committing to main:**
```
========================================
   Committed to main branch
========================================

💡 Tip: After pushing, run './scripts/deploy.sh' to deploy changes
```

**Before pushing to main:**
```
========================================
   ⚠️  Pushing to main branch
========================================

After push completes, you can deploy with:
  ./scripts/deploy.sh

This will auto-detect changes and deploy:
  • Frontend (if frontend/ changed)
  • Backend (if BackEndApi/ changed)
  • Infrastructure (if terraform/ changed)
```

### Local Testing

#### Frontend
```bash
cd frontend
npm start  # Development server on http://localhost:3000
```

#### Backend
```bash
cd BackEndApi
docker-compose -f local.yml up
# Backend on http://localhost:8000
```

## Monitoring & Debugging

### View Lambda Logs

```bash
# Task Manager logs
aws logs tail /aws/lambda/ProjectMaker}-task-manager-prod --follow

# Task Monitor logs
aws logs tail /aws/lambda/ProjectMaker}-task-monitor-prod --follow
```

### View ECS Task Logs

```bash
aws logs tail /ecs/ProjectMaker}-prod --follow
```

### Check Task State

```bash
aws dynamodb get-item \
  --table-name ProjectMaker}-task-state-prod \
  --key '{"task_id": {"S": "main"}}' \
  --output json | jq
```

### Monitor CloudWatch Alarm

```bash
# Check current alarm state
aws cloudwatch describe-alarms \
  --alarm-names ProjectMaker}-task-inactivity-prod

# View alarm history
aws cloudwatch describe-alarm-history \
  --alarm-name ProjectMaker}-task-inactivity-prod \
  --max-records 10

# View TaskPing metrics
aws cloudwatch get-metric-statistics \
  --namespace ProjectMaker}/ECS \
  --metric-name TaskPing \
  --dimensions Name=Environment,Value=prod \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Sum

# Manually trigger alarm (for testing)
aws cloudwatch set-alarm-state \
  --alarm-name ProjectMaker}-task-inactivity-prod \
  --state-value ALARM \
  --state-reason "Manual test"
```

### List Running Tasks

```bash
aws ecs list-tasks --cluster ProjectMaker}-prod
```

### Describe Task

```bash
aws ecs describe-tasks \
  --cluster ProjectMaker}-prod \
  --tasks <task-arn>
```

## Cost Breakdown

### Monthly Costs (Light Usage)

| Service | Usage | Cost |
|---------|-------|------|
| **Lambda** | 10k requests/month | Free tier |
| **API Gateway** | 10k requests/month | $0.01 |
| **ECS Fargate** | 1 hour/day @ 0.5vCPU, 1GB | $1.20 |
| **S3 Storage** | 1GB frontend + 100MB DB | $0.03 |
| **S3 Requests** | 100k GET, 1k PUT | $0.51 |
| **CloudFront** | 1GB transfer | $0.09 |
| **ECR Storage** | 500MB | $0.05 |
| **DynamoDB** | 1k reads, 100 writes | Free tier |
| **CloudWatch Logs** | 500MB | $0.25 |
| **Route53** | 1 hosted zone | $0.50 |

**Total**: ~$2.64/month

### Heavy Usage (10 hours/day backend)

- ECS: $12.14/month
- Everything else: ~$2/month
- **Total**: ~$14/month

## Troubleshooting

### Task Won't Start

1. Check Lambda logs for errors
2. Verify ECR has images: `aws ecr describe-images --repository-name ProjectMaker}-backend`
3. Check task definition: `aws ecs describe-task-definition --task-definition ProjectMaker}-backend-prod`

### Database Not Syncing

1. Check S3 bucket exists: `aws s3 ls s3://ProjectMaker}-database-prod/`
2. Verify task IAM role has S3 permissions
3. View task logs for sync errors

### Frontend Not Updating

1. Check S3 sync: `aws s3 ls s3://ProjectMaker}-frontend-prod/`
2. Verify CloudFront invalidation: `aws cloudfront list-invalidations --distribution-id <id>`
3. Clear browser cache

### Deployment Script Failing

1. Check environment variables are loaded: `echo $FRONTEND_S3_BUCKET`
2. Verify AWS credentials: `aws sts get-caller-identity`
3. Check AWS credentials have necessary permissions
4. Review script output for specific errors
5. Ensure Docker is running (for backend deployments)

## Cleanup

To destroy all infrastructure:

```bash
cd terraform/environments/prod
terraform destroy
```

**Warning**: This deletes everything including your database! Make sure to backup first:

```bash
aws s3 cp s3://ProjectMaker}-database-prod/db.sqlite3 ./backup-db.sqlite3
```

## Next Steps

- [ ] Set up custom domain with Route53
- [ ] Configure API authentication (Cognito/JWT)
- [ ] Enable S3 encryption at rest
- [ ] Set up CloudWatch alarms
- [ ] Configure automated backups
- [ ] Add staging environment
- [ ] Implement blue-green deployments

## Support

- **Deployment Scripts**: [scripts/README.md](scripts/README.md)
- **Terraform Docs**: [terraform/README.md](terraform/README.md)
- **Quick Start**: [DEPLOYMENT_QUICKSTART.md](DEPLOYMENT_QUICKSTART.md)
- **AWS Support**: Check CloudWatch Logs first
