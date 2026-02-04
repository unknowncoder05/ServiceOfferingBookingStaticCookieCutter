# Deployment Scripts

Automated deployment scripts for StoryArchitect using local git-based workflows.

## 🚀 Quick Start

### 1. Install Git Hooks (One-time setup)

```bash
./scripts/install-hooks.sh
```

This installs git hooks that remind you to deploy after pushing to `main`.

### 2. Deploy Changes

After committing and pushing to main:

```bash
./scripts/deploy.sh
```

This script automatically:
- Detects what changed (frontend/backend/infrastructure)
- Deploys only the changed components
- Tracks deployment history

## 📂 Available Scripts

| Script | Description | Usage |
|--------|-------------|-------|
| `deploy.sh` | **Master script** - Auto-detects changes and deploys | `./scripts/deploy.sh` |
| `deploy-frontend.sh` | Deploy React frontend to S3 + CloudFront | `./scripts/deploy-frontend.sh` |
| `deploy-backend.sh` | Build and push Docker image to ECR | `./scripts/deploy-backend.sh` |
| `deploy-infrastructure.sh` | Apply Terraform changes | `./scripts/deploy-infrastructure.sh [plan\|apply\|destroy]` |
| `install-hooks.sh` | Install git hooks for deployment prompts | `./scripts/install-hooks.sh` |

## 🔧 Configuration

### Environment Variables

Set these in your shell profile (`~/.bashrc`, `~/.zshrc`, etc.):

```bash
# AWS Configuration
export AWS_REGION=us-east-1
export AWS_PROFILE=default  # or your AWS profile name

# S3 & CloudFront (from Terraform outputs)
export FRONTEND_S3_BUCKET=storyarchitect-frontend-prod
export CLOUDFRONT_DISTRIBUTION_ID=E1234567890ABC
export DATABASE_S3_BUCKET=storyarchitect-database-prod

# ECR
export ECR_REPOSITORY=storyarchitect-backend
```

Or create a `.env` file in the project root:

```bash
cat > .env <<EOF
export AWS_REGION=us-east-1
export FRONTEND_S3_BUCKET=storyarchitect-frontend-prod
export CLOUDFRONT_DISTRIBUTION_ID=E1234567890ABC
export DATABASE_S3_BUCKET=storyarchitect-database-prod
export ECR_REPOSITORY=storyarchitect-backend
EOF

# Load before deploying
source .env
```

**Important**: Add `.env` to `.gitignore` to keep credentials private!

## 📖 Workflow

### Typical Development Cycle

```bash
# 1. Make changes to your code
vim frontend/src/App.tsx

# 2. Commit changes
git add .
git commit -m "feat: update homepage"

# 3. Push to main
git push origin main

# 4. Deploy (auto-detects frontend changed)
./scripts/deploy.sh
```

### Deploy Specific Component

```bash
# Deploy frontend only
./scripts/deploy-frontend.sh

# Deploy backend only
./scripts/deploy-backend.sh

# Deploy infrastructure only
./scripts/deploy-infrastructure.sh plan   # Preview changes
./scripts/deploy-infrastructure.sh apply  # Apply changes
```

## 🎯 How Auto-Detection Works

The `deploy.sh` script:

1. **First run**: Asks what to deploy (no history)
2. **Subsequent runs**: Compares current commit with last deployment
   - Checks `git diff` for changes in:
     - `frontend/` → Deploy frontend
     - `BackEndApi/` → Deploy backend
     - `terraform/` → Deploy infrastructure
3. **Stores state**: Saves commit hash in `.last-deploy`

### Override Auto-Detection

Force deploy even if no changes:

```bash
./scripts/deploy.sh
# When prompted "No changes detected", choose 'y' to force deploy
```

## 📝 Detailed Script Behavior

### Frontend Deployment (`deploy-frontend.sh`)

**What it does:**
1. Installs npm dependencies
2. Builds React app
3. Syncs to S3 with optimized cache headers:
   - Static assets: 1-year cache
   - `index.html`: no cache
4. Creates CloudFront invalidation
5. Waits for invalidation to complete

**Requirements:**
- Node.js 18+
- AWS CLI configured
- `FRONTEND_S3_BUCKET` set
- `CLOUDFRONT_DISTRIBUTION_ID` set (optional)

**Time:** ~2-3 minutes

### Backend Deployment (`deploy-backend.sh`)

**What it does:**
1. Checks/creates ECR repository
2. Logs into ECR
3. Builds Docker image with Docker Buildx
4. Tags image with commit SHA + `latest`
5. Pushes both tags to ECR
6. Verifies upload

**Requirements:**
- Docker installed and running
- AWS CLI configured
- `ECR_REPOSITORY` set (optional, defaults to `storyarchitect-backend`)

**Time:** ~5-10 minutes (depending on image size)

**Note:** On-demand architecture means no ECS service update needed. New tasks automatically use `:latest`.

### Infrastructure Deployment (`deploy-infrastructure.sh`)

**What it does:**
1. Creates `terraform.tfvars` if missing
2. Runs `terraform init`
3. Validates configuration
4. Creates plan
5. **If `apply`**: Applies changes and shows outputs
6. **If `plan`**: Shows plan and exits

**Requirements:**
- Terraform 1.6+ installed
- AWS CLI configured
- Edit `terraform/environments/prod/terraform.tfvars` first!

**Actions:**
```bash
./scripts/deploy-infrastructure.sh plan     # Preview changes
./scripts/deploy-infrastructure.sh apply    # Apply changes
./scripts/deploy-infrastructure.sh destroy  # Destroy infrastructure
```

**Time:** ~3-15 minutes (depending on changes)

## 🎣 Git Hooks

### Post-Commit Hook

Triggers after `git commit` on `main` branch.

**Does:**
- Reminds you to deploy after committing

**Output:**
```
========================================
   Committed to main branch
========================================

💡 Tip: After pushing, run './scripts/deploy.sh' to deploy changes
```

### Pre-Push Hook

Triggers before `git push` to `main` branch.

**Does:**
- Warns about pushing to main
- Shows deployment command

**Output:**
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

### Disabling Hooks

Remove hooks:
```bash
rm .git/hooks/post-commit
rm .git/hooks/pre-push
```

Re-install:
```bash
./scripts/install-hooks.sh
```

## 🔍 Troubleshooting

### AWS Credentials Not Found

```bash
Error: AWS credentials not configured
```

**Fix:**
```bash
aws configure
# Enter your Access Key ID, Secret Access Key, and region
```

### S3 Bucket Not Found

```bash
Error: FRONTEND_S3_BUCKET not set
```

**Fix:**
1. Deploy infrastructure first:
   ```bash
   ./scripts/deploy-infrastructure.sh apply
   ```
2. Get bucket name from outputs:
   ```bash
   cd terraform/environments/prod
   terraform output frontend_bucket_name
   ```
3. Export it:
   ```bash
   export FRONTEND_S3_BUCKET=<bucket-name>
   ```

### Docker Not Running

```bash
Error: Cannot connect to Docker daemon
```

**Fix:**
```bash
# macOS/Linux
sudo service docker start

# macOS with Docker Desktop
open -a Docker
```

### Terraform State Locked

```bash
Error: Error acquiring the state lock
```

**Fix:**
```bash
cd terraform/environments/prod
terraform force-unlock <lock-id>
```

### CloudFront Invalidation Timeout

If `deploy-frontend.sh` hangs on CloudFront invalidation:

**Fix:**
- Press `Ctrl+C` (invalidation continues in background)
- Or wait ~1-2 minutes for completion
- Or skip wait: comment out `aws cloudfront wait` in script

## 💡 Best Practices

### 1. Always Test Infrastructure Changes

```bash
# Always plan first!
./scripts/deploy-infrastructure.sh plan

# Review changes, then apply
./scripts/deploy-infrastructure.sh apply
```

### 2. Use Feature Branches

```bash
# Develop on feature branches
git checkout -b feature/new-feature

# Merge to main when ready
git checkout main
git merge feature/new-feature

# Deploy
./scripts/deploy.sh
```

### 3. Backup Database Before Infrastructure Changes

```bash
# Backup SQLite DB from S3
aws s3 cp s3://$DATABASE_S3_BUCKET/db.sqlite3 ./backup-$(date +%Y%m%d).sqlite3
```

### 4. Monitor Deployments

```bash
# Frontend: Check CloudFront
aws cloudfront get-distribution --id $CLOUDFRONT_DISTRIBUTION_ID

# Backend: Check ECR
aws ecr describe-images --repository-name $ECR_REPOSITORY

# Infrastructure: Check Terraform state
cd terraform/environments/prod && terraform show
```

## 📊 Deployment Times

| Component | Typical Time | Notes |
|-----------|-------------|-------|
| Frontend | 2-3 minutes | Includes build + S3 sync + CloudFront invalidation |
| Backend | 5-10 minutes | Docker build time varies by image size |
| Infrastructure (plan) | 30 seconds | Quick validation |
| Infrastructure (apply) | 3-15 minutes | Depends on resources being created/updated |
| **Full deployment** | 10-20 minutes | All three components |

## 🆘 Support

If scripts fail:

1. **Check logs** - Scripts output detailed error messages
2. **Verify AWS credentials** - `aws sts get-caller-identity`
3. **Check AWS region** - `echo $AWS_REGION`
4. **Verify prerequisites** - Docker, Terraform, Node.js installed
5. **Review AWS Console** - Check S3, ECR, CloudFront, etc.

## 📚 See Also

- [INFRASTRUCTURE.md](../INFRASTRUCTURE.md) - Complete infrastructure guide
- [terraform/README.md](../terraform/README.md) - Terraform documentation
- [DEPLOYMENT_QUICKSTART.md](../DEPLOYMENT_QUICKSTART.md) - Quick setup guide
