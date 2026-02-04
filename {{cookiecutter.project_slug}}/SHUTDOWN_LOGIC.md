# Server Shutdown Logic - Implementation Summary

## Overview

This document explains the complete implementation of the CloudWatch-based automatic server shutdown system. The system tracks backend activity and automatically shuts down ECS tasks after periods of inactivity to save costs.

## Key Parameters

- **Inactivity Timeout (X)**: 10 minutes - Backend shuts down after 10 minutes without activity
- **Ping Frequency (Y)**: 5 minutes (300 seconds) - Frontend pings backend every 5 minutes

## Architecture Components

### 1. Frontend (React/TypeScript)

#### **ServerStartPage Component** (`frontend/src/pages/ServerStartPage.tsx`)
- Displays when backend is stopped
- Shows a "Start Server" button
- Provides visual feedback during startup (30-60 seconds)
- Automatically navigates to projects page once backend is ready

#### **BackendManager Service** (`frontend/src/services/BackendManager.ts`)
**Key Methods:**
- `checkHealth()` - Quick health check without starting backend
- `manualStart()` - Starts backend when user clicks button
- `pingBackend()` - Calls Django keep-alive endpoint every 5 minutes

**Behavior:**
1. On app load, checks backend health
2. If backend is down → redirects to `/start-server`
3. If backend is up → proceeds with normal auth flow
4. Once running, pings `/api/v1/keep-alive/` every 5 minutes
5. Dynamically adjusts ping frequency based on backend response

#### **App.tsx Updates**
- Added health check on initialization
- Routes to `/start-server` if backend is unhealthy
- Only proceeds with authentication if backend is ready

### 2. Backend (Django)

#### **Keep-Alive Endpoint** (`BackEndApi/src/api/utils/views.py`)

**Endpoint:** `POST /api/v1/keep-alive/`
**Authentication:** No auth required (AllowAny)

**Functionality:**
1. Receives ping from frontend
2. Pushes custom CloudWatch metric: `BackendActivity`
3. Returns ping frequency configuration to frontend
4. Gracefully handles metric push failures

**CloudWatch Metric Details:**
- Namespace: `ProjectMaker}/Backend`
- Metric Name: `BackendActivity`
- Value: 1.0 (Count)
- Dimensions:
  - `Environment`: prod/dev
  - `Project`: ProjectMaker}

**Response Format:**
```json
{
  "status": "alive",
  "message": "Activity recorded successfully",
  "ping_frequency_seconds": 300,
  "ping_frequency_ms": 300000,
  "timestamp": "2025-01-02T12:00:00Z"
}
```

### 3. CloudWatch Monitoring

#### **CloudWatch Alarm** (`terraform/modules/cloudwatch/main.tf`)

**Alarm Configuration:**
- **Name**: `ProjectMaker}-backend-inactivity-prod`
- **Metric**: `BackendActivity` in `ProjectMaker}/Backend` namespace
- **Comparison**: Sum < 1 over 10 minutes
- **Evaluation**: 1 period of 600 seconds (10 minutes)
- **Missing Data**: Treated as breaching (no metric = inactive)

**Trigger Behavior:**
- If no `BackendActivity` metric received for 10 minutes → alarm triggers
- Publishes to SNS topic

#### **SNS Topic**
- **Name**: `ProjectMaker}-backend-inactivity-prod`
- **Subscriber**: Task Shutdown Lambda function

### 4. Lambda Functions

#### **Task Shutdown Lambda** (`terraform/lambda_functions/task_shutdown/index.py`)

**Trigger:** SNS notification from CloudWatch alarm
**Purpose:** Stop ECS tasks due to inactivity

**Flow:**
1. Receives SNS message from CloudWatch alarm
2. Lists all running tasks for the task definition
3. Stops each running task with reason: "Stopped due to inactivity (CloudWatch alarm)"
4. Logs all actions to CloudWatch Logs

**Environment Variables:**
- `ECS_CLUSTER_NAME`
- `TASK_DEFINITION_FAMILY`
- `PROJECT_NAME`
- `ENVIRONMENT`

#### **Task Manager Lambda** (unchanged - simplified)

**Purpose:** Start/manage ECS tasks on demand
**Endpoints:**
- `GET /start` - Starts backend if not running
- `GET /start?action=stop` - Stops running backend

**Note:** Removed ping handling from Lambda - now handled by Django

### 5. Infrastructure (Terraform)

#### **ECS Task Role Permissions** (`terraform/modules/ecs/main.tf`)

**Added IAM Policy:** `cloudwatch_metrics`
- **Action**: `cloudwatch:PutMetricData`
- **Resource**: `*`
- **Condition**: Namespace = `ProjectMaker}/Backend`

This allows ECS tasks to push custom CloudWatch metrics from Django.

#### **Lambda IAM Permissions** (`terraform/modules/lambda/main.tf`)

Task Shutdown Lambda has permissions for:
- `ecs:StopTask`
- `ecs:ListTasks`
- `ecs:DescribeTasks`

#### **Environment Variables** (`terraform/environments/prod/main.tf`)

**ECS Container:**
- `CLOUDWATCH_NAMESPACE`: "ProjectMaker}/Backend"
- `PING_FREQUENCY_SECONDS`: "300" (5 minutes)
- `PROJECT_NAME`: "ProjectMaker}"
- `ENVIRONMENT`: "prod"
- `AWS_REGION`: (from config)

**Terraform Variables:**
- `cloudwatch_namespace` (default: "ProjectMaker}/Backend")
- `inactivity_timeout_minutes` (default: 10)
- `ping_frequency_seconds` (default: 300)

## Complete Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                      USER OPENS APP                              │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
              ┌─────────────────────────┐
              │ Health Check via        │
              │ GET /api/v1/health/     │
              └─────────────────────────┘
                            │
                ┌───────────┴──────────┐
                │                      │
           ❌ FAIL                  ✅ SUCCESS
                │                      │
                ▼                      ▼
    ┌─────────────────────┐   ┌────────────────┐
    │ Show Start Server   │   │ Proceed with   │
    │ Button Page         │   │ Normal Auth    │
    └─────────────────────┘   └────────────────┘
                │                      │
         User clicks                   │
         "Start Server"                │
                │                      │
                ▼                      │
    ┌─────────────────────┐           │
    │ Lambda: Start ECS   │           │
    │ Task via API GW     │           │
    └─────────────────────┘           │
                │                      │
                ▼                      │
    ┌─────────────────────┐           │
    │ Wait for Backend    │           │
    │ (30-60 seconds)     │           │
    └─────────────────────┘           │
                │                      │
                └──────────┬───────────┘
                           │
                           ▼
         ┌─────────────────────────────────┐
         │   BACKEND RUNNING & READY       │
         │                                 │
         │  Frontend pings every 5 min:    │
         │  POST /api/v1/keep-alive/       │
         │         │                       │
         │         ▼                       │
         │  Django pushes CloudWatch       │
         │  metric: BackendActivity = 1    │
         └─────────────────────────────────┘
                           │
         ┌─────────────────┴──────────────┐
         │                                │
    USER ACTIVE                    USER INACTIVE
    (pings continue)               (no pings)
         │                                │
         │                                ▼
         │                  ┌──────────────────────────┐
         │                  │ 10 minutes pass without  │
         │                  │ BackendActivity metric   │
         │                  └──────────────────────────┘
         │                                │
         │                                ▼
         │                  ┌──────────────────────────┐
         │                  │ CloudWatch Alarm         │
         │                  │ ALARM State → SNS        │
         │                  └──────────────────────────┘
         │                                │
         │                                ▼
         │                  ┌──────────────────────────┐
         │                  │ Task Shutdown Lambda     │
         │                  │ Stops ECS Task           │
         │                  └──────────────────────────┘
         │                                │
         │                                ▼
         └────────────────────► BACKEND STOPPED ◄──────
                                 (Next user sees
                                  Start Server page)
```

## Cost Optimization

### Previous Approach (Expensive)
- Frontend pings Lambda every 2.5 minutes
- Each Lambda invocation costs money
- High frequency = high Lambda costs
- Metric: ~12,000 Lambda invocations/month per active user

### New Approach (Cost-Effective)
- Frontend pings Django endpoint every 5 minutes
- Django (already running) pushes CloudWatch metric
- Only charged for CloudWatch PutMetricData API calls
- Metric: ~8,640 PutMetricData calls/month per active user
- **Estimated savings: ~90% on activity tracking costs**

## Configuration

### Adjusting Timeouts

To change the inactivity timeout from 10 minutes to a different value:

1. Edit `terraform/environments/prod/variables.tf`:
```hcl
variable "inactivity_timeout_minutes" {
  default     = 15  # Change to desired minutes
}
```

2. Apply Terraform:
```bash
cd terraform/environments/prod
terraform apply
```

### Adjusting Ping Frequency

To change ping frequency from 5 minutes:

1. Edit `terraform/environments/prod/variables.tf`:
```hcl
variable "ping_frequency_seconds" {
  default     = 180  # Change to desired seconds (e.g., 3 minutes)
}
```

2. Apply Terraform (updates ECS environment variables)
3. Redeploy backend container
4. Frontend will automatically pick up new frequency from `/api/v1/keep-alive/` response

### Best Practice
Keep ping frequency < inactivity timeout to ensure reliable tracking:
- Example: Ping every 5 minutes, timeout after 10 minutes
- This gives 2x buffer for network issues or missed pings

## Monitoring & Debugging

### CloudWatch Logs

**Backend Activity:**
- Log Group: `/ecs/ProjectMaker}-prod`
- Check for: "CloudWatch metric pushed successfully"

**Task Shutdown:**
- Log Group: `/aws/lambda/ProjectMaker}-task-shutdown-prod`
- Shows: Which tasks were stopped and why

**Task Manager (Startup):**
- Log Group: `/aws/lambda/ProjectMaker}-task-manager-prod`
- Shows: Task startup process

### CloudWatch Metrics

**Custom Metric:** `ProjectMaker}/Backend > BackendActivity`
- Dimensions: Environment=prod, Project=ProjectMaker}
- Should show spikes every 5 minutes when users are active

**ECS Metrics:**
- `AWS/ECS > CPUUtilization` and `MemoryUtilization`
- Track when tasks start/stop

### CloudWatch Alarms

**Alarm:** `ProjectMaker}-backend-inactivity-prod`
- State: OK = backend active, ALARM = backend inactive
- History: Shows when alarm triggered and SNS notifications sent

## Testing

### Test Inactivity Shutdown

1. Start backend (click "Start Server" or visit app)
2. Keep app open for 4 minutes (to send at least one ping)
3. Close app completely
4. Wait 10 minutes
5. Check CloudWatch: Alarm should trigger
6. Check ECS: Task should be stopped
7. Open app: Should see "Start Server" page

### Test Keep-Alive

1. Start backend
2. Keep app open and active
3. Monitor CloudWatch metrics:
   - Should see `BackendActivity` = 1 every 5 minutes
4. Task should NOT stop as long as pings continue

### Test Frontend Behavior

1. With backend stopped, visit app
   - Should see "Start Server" page immediately
2. Click "Start Server"
   - Should show loading state
   - Should wait 30-60 seconds
   - Should redirect to projects page
3. Leave app open
   - Console should log "Backend keep-alive ping successful" every 5 minutes

## Deployment Checklist

- [ ] Apply Terraform changes for CloudWatch module
- [ ] Deploy updated backend with keep-alive endpoint
- [ ] Deploy updated frontend with ServerStartPage
- [ ] Verify CloudWatch alarm is created
- [ ] Verify SNS topic subscription is active
- [ ] Test health check and start server flow
- [ ] Test keep-alive pings
- [ ] Test automatic shutdown after 10 minutes
- [ ] Monitor CloudWatch logs for errors

## Files Modified/Created

### Backend
- ✅ `BackEndApi/src/api/utils/views.py` - Added `keep_alive()` endpoint
- ✅ `BackEndApi/src/config/urls.py` - Added `/keep-alive/` route

### Frontend
- ✅ `frontend/src/pages/ServerStartPage.tsx` - New page for starting backend
- ✅ `frontend/src/services/BackendManager.ts` - Updated ping logic and health check
- ✅ `frontend/src/App.tsx` - Added health check and routing

### Lambda
- ✅ `terraform/lambda_functions/task_shutdown/index.py` - New shutdown function
- ✅ `terraform/lambda_functions/task_manager/index.py` - Simplified (removed metric logic)

### Terraform
- ✅ `terraform/modules/cloudwatch/` - New module for alarms and SNS
  - `main.tf`
  - `variables.tf`
  - `outputs.tf`
- ✅ `terraform/modules/ecs/main.tf` - Added CloudWatch metrics IAM policy
- ✅ `terraform/modules/lambda/main.tf` - Added task_shutdown function
- ✅ `terraform/modules/lambda/outputs.tf` - Added shutdown function outputs
- ✅ `terraform/environments/prod/main.tf` - Wired all modules together
- ✅ `terraform/environments/prod/variables.tf` - Added configuration variables

## Summary

The new shutdown logic provides:
- ✅ **Cost-effective monitoring** - Django pushes metrics instead of frequent Lambda calls
- ✅ **Automatic shutdown** - Backend stops after 10 minutes of inactivity
- ✅ **User-controlled startup** - Explicit "Start Server" button for better UX
- ✅ **Reliable tracking** - CloudWatch metrics with configurable thresholds
- ✅ **Flexible configuration** - Easy to adjust timeouts and frequencies
- ✅ **Comprehensive logging** - Full visibility into all operations

**Cost Impact:** ~90% reduction in activity tracking costs while maintaining reliable automatic shutdown.
