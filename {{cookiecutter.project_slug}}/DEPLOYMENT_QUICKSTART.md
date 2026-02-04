# ProjectMaker} Deployment Quick Start

## TL;DR - Get Running in 10 Minutes

### 1. Configure Terraform (2 min)

```bash
cd terraform/environments/prod
cp terraform.tfvars.example terraform.tfvars
```

Edit `terraform.tfvars` - **minimum required**:
```hcl
aws_region           = "us-east-1"
frontend_bucket_name = "ProjectMaker}-frontend-yourname"  # Must be unique!
database_bucket_name = "ProjectMaker}-database-yourname"  # Must be unique!
```

### 2. Deploy Infrastructure (5 min)

```bash
terraform init
terraform apply  # Type 'yes' when prompted
```

Save these outputs:
- `frontend_bucket_name`
- `cloudfront_distribution_id`
- `ecr_repository_url`
- `api_start_endpoint`

### 3. Get Deployment Credentials (1 min)

Retrieve automatically-created deployment credentials:

```bash
./scripts/get-deployment-credentials.sh
```

Choose option 1 to create AWS CLI profile `ProjectMaker}-deployment`.

### 4. Configure Environment Variables (1 min)

Create a `.env` file in project root:

```bash
cat > .env <<EOF
export AWS_REGION=us-east-1
export AWS_PROFILE=ProjectMaker}-deployment
export FRONTEND_S3_BUCKET=$(cd terraform/environments/prod && terraform output -raw frontend_bucket_name)
export CLOUDFRONT_DISTRIBUTION_ID=$(cd terraform/environments/prod && terraform output -raw cloudfront_distribution_id)
export DATABASE_S3_BUCKET=$(cd terraform/environments/prod && terraform output -raw database_bucket_name)
export ECR_REPOSITORY=ProjectMaker}-backend
EOF

# Add to .gitignore
echo ".env" >> .gitignore

# Load variables
source .env
```

### 5. Install Git Hooks (30 sec)

```bash
./scripts/install-hooks.sh
```

This installs hooks that remind you to deploy after committing to main.

### 6. Deploy Everything (2-5 min)

```bash
# Load environment variables
source .env

# Deploy all components
./scripts/deploy.sh
```

The script will:
1. Ask what to deploy (on first run)
2. Deploy infrastructure → backend → frontend
3. Save deployment state for future auto-detection

**Or deploy individually:**

```bash
# Backend only
./scripts/deploy-backend.sh

# Frontend only
./scripts/deploy-frontend.sh

# Infrastructure only
./scripts/deploy-infrastructure.sh apply
```

## Testing

### Start Backend
```bash
curl $(cd terraform/environments/prod && terraform output -raw api_start_endpoint)
```

Response:
```json
{
  "status": "started",
  "public_ip": "54.xxx.xxx.xxx"
}
```

Wait 60 seconds, then:
```bash
curl http://54.xxx.xxx.xxx:8000/api/story/projects/
```

### Access Frontend
```bash
echo "Frontend URL: https://$(cd terraform/environments/prod && terraform output -raw cloudfront_domain)"
```

## Deployment Workflow

After the initial setup, deploying is simple:

```bash
# 1. Make changes
vim frontend/src/App.tsx

# 2. Commit
git add .
git commit -m "feat: update UI"

# 3. Push
git push origin main

# 4. Deploy (auto-detects changes)
source .env
./scripts/deploy.sh
```

The `deploy.sh` script:
- **Detects changes**: Compares with last deployment
- **Deploys selectively**: Only deploys what changed
  - `frontend/` → Deploys to S3 + CloudFront
  - `BackEndApi/` → Builds and pushes to ECR
  - `terraform/` → Runs terraform apply
- **Tracks state**: Saves commit hash for next time

## Common Commands

### View Logs
```bash
# Task Manager Lambda logs (handles /start requests)
aws logs tail /aws/lambda/ProjectMaker}-task-manager-prod --follow

# Task Monitor Lambda logs (triggered by alarm)
aws logs tail /aws/lambda/ProjectMaker}-task-monitor-prod --follow

# Backend ECS logs
aws logs tail /ecs/ProjectMaker}-prod --follow
```

### Monitor Alarm
```bash
# Check if alarm is active
aws cloudwatch describe-alarms --alarm-names ProjectMaker}-task-inactivity-prod

# Manually trigger alarm (for testing)
aws cloudwatch set-alarm-state \
  --alarm-name ProjectMaker}-task-inactivity-prod \
  --state-value ALARM \
  --state-reason "Manual test"
```

### Manual Operations
```bash
# Start backend
curl https://<api-url>/start

# Extend backend lifetime (ping)
curl https://<api-url>/start?action=ping

# Stop backend (it auto-stops after 5 min idle)
aws ecs stop-task --cluster ProjectMaker}-prod --task <task-arn>
```

### Database Operations
```bash
# Backup database
aws s3 cp s3://ProjectMaker}-database-prod/db.sqlite3 ./backup.sqlite3

# Restore database
aws s3 cp ./backup.sqlite3 s3://ProjectMaker}-database-prod/db.sqlite3

# List backups
aws s3api list-object-versions --bucket ProjectMaker}-database-prod --prefix db.sqlite3
```

## Cost Estimate

**Light usage** (1 hour/day backend): **$2-3/month**

**Heavy usage** (10 hours/day backend): **$12-15/month**

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Task won't start | Check Lambda logs: `aws logs tail /aws/lambda/ProjectMaker}-task-manager-prod` |
| Frontend not updating | Invalidate CloudFront: `aws cloudfront create-invalidation --distribution-id <id> --paths "/*"` |
| Database not syncing | Check task logs: `aws logs tail /ecs/ProjectMaker}-prod` |
| Deploy script failing | Check environment variables: `echo $FRONTEND_S3_BUCKET`, verify AWS credentials: `aws sts get-caller-identity` |
| Docker build fails | Ensure Docker is running: `docker ps` |

## Full Documentation

- **Complete Guide**: `INFRASTRUCTURE.md`
- **Deployment Scripts**: `scripts/README.md`
- **Terraform Docs**: `terraform/README.md`
- **Architecture Diagrams**: See `INFRASTRUCTURE.md`

## Support

1. Check CloudWatch Logs
2. Review Terraform outputs: `terraform output`
3. Review deployment script output for errors
4. Consult AWS documentation

## Cleanup

```bash
# Backup database first!
aws s3 cp s3://ProjectMaker}-database-prod/db.sqlite3 ./backup-$(date +%Y%m%d).sqlite3

# Destroy all infrastructure
cd terraform/environments/prod
terraform destroy
```
