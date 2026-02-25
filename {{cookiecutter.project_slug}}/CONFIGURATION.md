# Configuration Guide - Avoiding Hardcoded Values

This document describes all configurable values in the MyProject application and where to set them.

## Frontend Configuration

### Environment Variables

All frontend configuration is in `/frontend/.env.local` (copy from `.env.example`):

```bash
# API Configuration
REACT_APP_API_GATEWAY_START_ENDPOINT=   # API Gateway endpoint
REACT_APP_API_URL=                      # Base API URL
REACT_APP_BACKEND_PORT=8000             # Backend server port
REACT_APP_API_BASE_PATH=/api/v1         # API base path

# Keep-Alive & Monitoring
REACT_APP_KEEP_ALIVE_INTERVAL=300000    # Ping frequency (ms)
REACT_APP_STARTUP_TIMEOUT=90000         # Backend startup timeout (ms)
REACT_APP_HEALTH_CHECK_TIMEOUT=5000     # Health check timeout (ms)
REACT_APP_POLLING_INTERVAL=2000         # Polling interval (ms)
REACT_APP_NAVIGATION_DELAY=1000         # Navigation delay (ms)
```

### Configuration File

All values are centralized in `frontend/src/config/environment.ts`:

- ✅ No hardcoded URLs
- ✅ No hardcoded timeouts
- ✅ No hardcoded ports
- ✅ All values have sensible defaults
- ✅ All values can be overridden via environment variables

## Backend Configuration (Django)

### Environment Variables

Set these in your ECS task definition or `.env` file:

```bash
# AWS Configuration
AWS_REGION=us-east-1                    # AWS region for CloudWatch

# CloudWatch Monitoring
CLOUDWATCH_NAMESPACE=MyProject/Backend  # CloudWatch namespace
PING_FREQUENCY_SECONDS=300              # How often frontend should ping
PROJECT_NAME=MyProject             # Project name
ENVIRONMENT=prod                        # Environment name

# Application Settings
# (Add Django-specific settings here)
```

### Notes
- AWS region has fallback to `us-east-1` in code (standard AWS default)
- All other values use `os.environ.get()` with sensible defaults

## Lambda Configuration

### Task Manager Lambda

Environment variables (set in Terraform):

```python
ECS_CLUSTER_NAME        # ECS cluster name
TASK_DEFINITION_FAMILY  # Task definition family
SUBNET_IDS              # Comma-separated subnet IDs
SECURITY_GROUP_ID       # Security group ID
API_GATEWAY_ID          # API Gateway ID
API_INTEGRATION_ID      # API Gateway integration ID
BACKEND_PORT           # Backend port (default: 8000)
TASK_LIFETIME_SECONDS  # Task lifetime (default: 300)
PROJECT_NAME           # Project name
ENVIRONMENT            # Environment name
```

### Task Shutdown Lambda

Environment variables (set in Terraform):

```python
ECS_CLUSTER_NAME        # ECS cluster name
TASK_DEFINITION_FAMILY  # Task definition family
PROJECT_NAME           # Project name
ENVIRONMENT            # Environment name
```

## Terraform Configuration

### Main Configuration File

`terraform/environments/prod/variables.tf`:

```hcl
# CloudWatch Configuration
variable "cloudwatch_namespace" {
  default = "MyProject/Backend"
}

variable "inactivity_timeout_minutes" {
  default = 10  # X = 10 minutes
}

variable "ping_frequency_seconds" {
  default = 300  # Y = 5 minutes
}

# Backend Configuration
variable "backend_port" {
  default = "8000"
}

# ECS Configuration
variable "ecs_task_cpu" {
  default = "512"
}

variable "ecs_task_memory" {
  default = "1024"
}

variable "task_lifetime_seconds" {
  default = 300
}

# Domain Configuration
variable "hosted_zone_name" {
  default = ""  # Set to your domain
}

variable "frontend_subdomain" {
  default = ""  # Set to your frontend subdomain
}

variable "api_subdomain" {
  default = ""  # Set to your API subdomain
}
```

### Environment-Specific Override

Create a `terraform.tfvars` file for environment-specific values:

```hcl
# terraform/environments/prod/terraform.tfvars
hosted_zone_name = "yerson.co"
frontend_subdomain = "MyProject"
api_subdomain = "apiMyProject"
inactivity_timeout_minutes = 15  # Override default
ping_frequency_seconds = 240      # Override default
```

## Configuration Dependencies

### Relationship Between Values

1. **Ping Frequency < Inactivity Timeout**
   - `REACT_APP_KEEP_ALIVE_INTERVAL` < `inactivity_timeout_minutes * 60 * 1000`
   - Example: 5 minutes (300s) < 10 minutes (600s)
   - Ensures at least 1-2 pings before timeout

2. **Health Check Timeout < Startup Timeout**
   - `REACT_APP_HEALTH_CHECK_TIMEOUT` < `REACT_APP_STARTUP_TIMEOUT`
   - Ensures multiple health check attempts during startup

3. **Polling Interval < Startup Timeout**
   - `REACT_APP_POLLING_INTERVAL` < `REACT_APP_STARTUP_TIMEOUT`
   - Ensures multiple polling attempts

4. **Backend Port Consistency**
   - Frontend `REACT_APP_BACKEND_PORT`
   - Lambda `BACKEND_PORT`
   - ECS container port
   - All must match (default: 8000)

## Configuration Checklist

### Frontend Deployment

- [ ] Copy `.env.example` to `.env.local`
- [ ] Set `REACT_APP_API_GATEWAY_START_ENDPOINT`
- [ ] Set `REACT_APP_API_URL` (optional, dynamically overridden)
- [ ] Adjust timeouts if needed
- [ ] Verify port matches backend

### Backend Deployment

- [ ] Set `AWS_REGION` in ECS environment
- [ ] Set `CLOUDWATCH_NAMESPACE`
- [ ] Set `PING_FREQUENCY_SECONDS` (should match frontend)
- [ ] Set `PROJECT_NAME` and `ENVIRONMENT`
- [ ] Configure Django settings (SECRET_KEY, DB, etc.)

### Terraform Deployment

- [ ] Review `terraform/environments/prod/variables.tf` defaults
- [ ] Create `terraform.tfvars` with overrides
- [ ] Set domain configuration
- [ ] Adjust timeouts if needed
- [ ] Run `terraform plan` to review changes
- [ ] Run `terraform apply` to deploy

## Common Configuration Scenarios

### Scenario 1: Local Development

**Frontend:**
```bash
REACT_APP_API_GATEWAY_START_ENDPOINT=  # Leave empty
REACT_APP_API_URL=http://localhost:8000/api/v1
```

**Backend:**
```bash
# Run Django locally
python manage.py runserver
```

### Scenario 2: Production with On-Demand Backend

**Frontend:**
```bash
REACT_APP_API_GATEWAY_START_ENDPOINT=https://apiMyProject.yerson.co/start
REACT_APP_API_URL=https://apiMyProject.yerson.co/api/v1
REACT_APP_KEEP_ALIVE_INTERVAL=300000  # 5 minutes
```

**Terraform:**
```hcl
inactivity_timeout_minutes = 10
ping_frequency_seconds = 300
```

### Scenario 3: Different Backend Port

If using port 3000 instead of 8000:

**Frontend:**
```bash
REACT_APP_BACKEND_PORT=3000
```

**Terraform:**
```hcl
backend_port = "3000"
```

**ECS:** Update container port mapping in task definition

### Scenario 4: Faster Shutdown (Testing)

**Terraform:**
```hcl
inactivity_timeout_minutes = 2   # 2 minutes
ping_frequency_seconds = 60       # 1 minute
```

**Frontend:**
```bash
REACT_APP_KEEP_ALIVE_INTERVAL=60000  # 1 minute
```

## Validation

### Check Configuration Consistency

Run this script to validate configuration:

```bash
#!/bin/bash
# validate-config.sh

# Frontend
FRONTEND_PING=$(grep KEEP_ALIVE_INTERVAL frontend/.env.local | cut -d= -f2)
FRONTEND_PORT=$(grep BACKEND_PORT frontend/.env.local | cut -d= -f2)

# Terraform
TF_PING=$(grep 'ping_frequency_seconds.*=' terraform/environments/prod/terraform.tfvars | cut -d= -f2 | tr -d ' ')
TF_PORT=$(grep 'backend_port.*=' terraform/environments/prod/terraform.tfvars | cut -d= -f2 | tr -d ' "')

# Convert frontend ms to seconds
FRONTEND_PING_SEC=$((FRONTEND_PING / 1000))

echo "Frontend ping: ${FRONTEND_PING_SEC}s"
echo "Terraform ping: ${TF_PING}s"
echo "Match: $([ "$FRONTEND_PING_SEC" = "$TF_PING" ] && echo "✓" || echo "✗")"

echo ""
echo "Frontend port: ${FRONTEND_PORT}"
echo "Terraform port: ${TF_PORT}"
echo "Match: $([ "$FRONTEND_PORT" = "$TF_PORT" ] && echo "✓" || echo "✗")"
```

## Troubleshooting

### Frontend not pinging backend

1. Check `REACT_APP_KEEP_ALIVE_INTERVAL` is set
2. Check browser console for ping logs
3. Verify backend `/api/v1/keep-alive/` endpoint is accessible

### Backend shutting down too quickly

1. Increase `inactivity_timeout_minutes` in Terraform
2. Decrease `ping_frequency_seconds` (ping more often)
3. Check CloudWatch metrics for `BackendActivity`
4. Review CloudWatch alarm history

### Backend not starting

1. Check `REACT_APP_API_GATEWAY_START_ENDPOINT` is set
2. Increase `REACT_APP_STARTUP_TIMEOUT`
3. Check Lambda logs for startup errors
4. Verify ECS task definition is valid

### Port mismatch errors

1. Ensure frontend `REACT_APP_BACKEND_PORT` matches
2. Ensure Lambda `BACKEND_PORT` matches
3. Ensure ECS container port mapping matches
4. Default is 8000 everywhere

## References

- Frontend config: `frontend/src/config/environment.ts`
- Backend views: `BackEndApi/src/api/utils/views.py`
- Lambda functions: `terraform/lambda_functions/*/index.py`
- Terraform variables: `terraform/environments/prod/variables.tf`
- Shutdown logic: `SHUTDOWN_LOGIC.md`
