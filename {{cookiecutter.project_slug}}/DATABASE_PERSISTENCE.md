# Database Persistence - How Database Saving Works

## Overview

MyProject uses SQLite as its database with **S3-based persistence** for the on-demand backend architecture. The database is synchronized between the ECS container and S3 bucket on startup and shutdown.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    S3 Bucket (Persistent)                    │
│           s3://MyProject-database-prod/                 │
│                    db.sqlite3                                │
└─────────────────────────────────────────────────────────────┘
                        ▲              │
                Download│              │Upload
                (Startup)              (Shutdown)
                        │              ▼
┌─────────────────────────────────────────────────────────────┐
│              ECS Container (Ephemeral)                       │
│                 /app/db.sqlite3                              │
│                                                              │
│  ┌──────────────────────────────────────────────────┐      │
│  │  Django Application (SQLite Database)            │      │
│  │  - Read/Write operations                         │      │
│  │  - Migrations                                    │      │
│  │  - All API operations                            │      │
│  └──────────────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

## Database Sync Script

### Location
`BackEndApi/compose/production/django/db-sync.sh`

### Functions

#### 1. **Download on Startup** (`download_db()`)
```bash
/db-sync.sh startup
```

**Process:**
1. Check if `DB_S3_BUCKET` is set
2. Check if database exists in S3: `s3://${DB_S3_BUCKET}/db.sqlite3`
3. If exists:
   - Download from S3 to `/app/db.sqlite3`
   - Create local backup: `/app/db.sqlite3.backup`
   - Set permissions: `chmod 644`
4. If not exists:
   - Start with fresh database
   - Django migrations will create schema

**Logs:**
```
[INFO] Checking for existing database in S3...
[INFO] Database found in S3. Downloading...
[INFO] Database downloaded successfully from s3://bucket/db.sqlite3
[INFO] Backup created at /app/db.sqlite3.backup
```

#### 2. **Upload on Shutdown** (`upload_db()`)
```bash
/db-sync.sh shutdown
```

**Process:**
1. Check if `DB_S3_BUCKET` is set
2. Check if local database exists at `/app/db.sqlite3`
3. Create timestamped backup in S3:
   - Format: `db.sqlite3.backup.20231202_143022`
   - Preserves previous version before overwrite
4. Upload current database to S3: `db.sqlite3`

**Logs:**
```
[INFO] Uploading database to S3...
[INFO] Creating timestamped backup in S3...
[INFO] Database uploaded successfully to s3://bucket/db.sqlite3
```

## Container Lifecycle

### Startup Sequence

**1. Docker Entrypoint** (`entrypoint.sh`)
```bash
#!/bin/bash
# Sync database on startup
/db-sync.sh startup

# Trap SIGTERM for graceful shutdown
trap 'echo "Received SIGTERM, syncing database..."; /db-sync.sh shutdown; exit 0' SIGTERM

# Start application in background
/start &
APP_PID=$!

# Wait for application process
wait $APP_PID
```

**2. Application Start** (`start`)
```bash
cd /app
python manage.py collectstatic --noinput
python manage.py migrate
python manage.py compilemessages
daphne config.asgi:application -b 0.0.0.0 -p 8000
```

**Complete Startup Flow:**
```
1. Container starts
2. Entrypoint runs → Downloads DB from S3
3. Django starts → Runs migrations
4. Application ready → Serves requests
5. Trap registered → Waits for SIGTERM
```

### Shutdown Sequence

**Graceful Shutdown (SIGTERM):**
```
1. ECS sends SIGTERM to container
2. Trap catches signal
3. Uploads DB to S3
4. Container exits with code 0
```

**Forceful Shutdown (SIGKILL after timeout):**
```
1. ECS sends SIGKILL (if SIGTERM timeout exceeded)
2. Container terminates immediately
3. ⚠️ Database NOT synced (data loss risk)
```

## S3 Configuration

### Terraform Setup

**S3 Bucket** (`terraform/modules/s3/main.tf`):
```hcl
resource "aws_s3_bucket" "database" {
  bucket = "MyProject-database-prod"
}

resource "aws_s3_bucket_versioning" "database" {
  bucket = aws_s3_bucket.database.id
  versioning_configuration {
    status = "Enabled"  # Keeps multiple versions
  }
}
```

**IAM Policy** (ECS task role):
```json
{
  "Effect": "Allow",
  "Action": [
    "s3:GetObject",
    "s3:PutObject",
    "s3:DeleteObject",
    "s3:ListBucket"
  ],
  "Resource": [
    "arn:aws:s3:::MyProject-database-prod",
    "arn:aws:s3:::MyProject-database-prod/*"
  ]
}
```

### Environment Variables

**ECS Task Definition:**
```json
{
  "environment": [
    {
      "name": "DB_S3_BUCKET",
      "value": "MyProject-database-prod"
    },
    {
      "name": "DB_S3_KEY",
      "value": "db.sqlite3"
    },
    {
      "name": "DB_LOCAL_PATH",
      "value": "/app/db.sqlite3"
    }
  ]
}
```

## Backup Strategy

### Automatic Backups

**1. Local Backup (On Download):**
- File: `/app/db.sqlite3.backup`
- When: Every container startup
- Purpose: Rollback if download corrupts

**2. S3 Timestamped Backups (On Upload):**
- File: `s3://bucket/db.sqlite3.backup.YYYYMMDD_HHMMSS`
- When: Every successful upload
- Purpose: Historical versions

**3. S3 Versioning:**
- Enabled on bucket
- Keeps all versions of `db.sqlite3`
- Can restore any previous version

### Manual Operations

**Download Database:**
```bash
# From container
docker exec <container-id> /db-sync.sh download

# Or directly with AWS CLI
aws s3 cp s3://MyProject-database-prod/db.sqlite3 ./db.sqlite3
```

**Upload Database:**
```bash
# From container
docker exec <container-id> /db-sync.sh upload

# Or directly with AWS CLI
aws s3 cp ./db.sqlite3 s3://MyProject-database-prod/db.sqlite3
```

**Restore from Backup:**
```bash
# List available backups
aws s3 ls s3://MyProject-database-prod/ | grep backup

# Restore specific backup
aws s3 cp s3://MyProject-database-prod/db.sqlite3.backup.20231202_143022 \
          s3://MyProject-database-prod/db.sqlite3
```

## Data Safety Considerations

### ✅ What Works Well

1. **Automatic sync on startup/shutdown**
   - Database always loaded from S3 on start
   - Changes saved to S3 on graceful stop

2. **Timestamped backups**
   - Every upload creates a backup
   - Can recover from accidental changes

3. **S3 versioning**
   - Multiple versions retained
   - Point-in-time recovery

4. **SIGTERM trap**
   - Graceful shutdown saves data
   - ECS gives 30 seconds for cleanup

### ⚠️ Potential Issues

#### 1. **Ungraceful Shutdown (SIGKILL)**

**Problem:**
- If container is forcefully killed (SIGKILL)
- If container crashes unexpectedly
- Database changes since last startup are lost

**Solution:**
Implement periodic sync (see improvements below)

#### 2. **Concurrent Access**

**Problem:**
- If multiple containers run simultaneously
- Last writer wins, data corruption possible

**Current Mitigation:**
- Task Manager Lambda ensures only 1 task runs
- Prevents concurrent access

#### 3. **Large Database Performance**

**Problem:**
- Upload/download time increases with DB size
- Startup/shutdown delays

**Current Status:**
- SQLite file is typically < 100MB
- Download/upload takes 1-3 seconds

## Improvements & Recommendations

### 1. **Periodic Database Sync**

Add periodic uploads to reduce data loss window:

**Implementation:**
Create a periodic sync script:

```bash
# /periodic-sync.sh
#!/bin/bash
while true; do
    sleep 300  # Every 5 minutes
    echo "[INFO] Periodic database sync..."
    /db-sync.sh upload
done
```

Update `entrypoint.sh`:
```bash
# Start periodic sync in background
/periodic-sync.sh &

# Start application
/start &
APP_PID=$!
wait $APP_PID
```

**Trade-offs:**
- ✅ Reduces data loss window to 5 minutes
- ✅ Survives crashes and SIGKILL
- ❌ Increases S3 API calls and costs
- ❌ Potential performance impact during sync

### 2. **Pre-Stop Hook**

Add ECS lifecycle hook for guaranteed shutdown sync:

**Terraform:**
```hcl
# In task definition
lifecycle {
  pre_stop {
    command = ["/db-sync.sh", "shutdown"]
    timeout = 30
  }
}
```

### 3. **Database Migration to RDS/Aurora Serverless**

For production scale:

**Benefits:**
- ✅ No sync logic needed
- ✅ Automatic backups
- ✅ Point-in-time recovery
- ✅ High availability
- ✅ Better performance

**Trade-offs:**
- ❌ Higher cost (~$50-100/month minimum)
- ❌ More complex setup
- ❌ Not serverless (always running)

### 4. **Write-Ahead Logging (WAL)**

Enable SQLite WAL mode for better concurrency:

**Django settings:**
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': '/app/db.sqlite3',
        'OPTIONS': {
            'init_command': 'PRAGMA journal_mode=WAL;',
        }
    }
}
```

**Considerations:**
- Must sync both `db.sqlite3` and `db.sqlite3-wal` files
- Update sync script to handle WAL files

## Monitoring

### CloudWatch Logs

**Check sync operations:**
```bash
aws logs tail /ecs/MyProject-prod --follow --filter-pattern "[INFO]"
```

**Look for:**
- `Database downloaded successfully`
- `Database uploaded successfully`
- `Failed to download/upload database`

### S3 Object Metadata

**Check last upload:**
```bash
aws s3api head-object \
  --bucket MyProject-database-prod \
  --key db.sqlite3
```

**Output:**
```json
{
  "LastModified": "2023-12-02T14:30:22+00:00",
  "ContentLength": 10485760,
  "ETag": "\"abc123...\""
}
```

### Backup Audit

**List all backups:**
```bash
aws s3 ls s3://MyProject-database-prod/ \
  | grep backup \
  | sort -r
```

## Troubleshooting

### Database Not Downloading

**Symptoms:**
- Fresh database on every startup
- Data loss between sessions

**Debug:**
```bash
# Check if S3 bucket exists
aws s3 ls s3://MyProject-database-prod/

# Check IAM permissions
aws s3 cp s3://MyProject-database-prod/db.sqlite3 /tmp/test.db

# Check container logs
aws logs tail /ecs/MyProject-prod --follow
```

### Database Not Uploading

**Symptoms:**
- Changes don't persist
- Database resets to old state

**Debug:**
```bash
# Check shutdown logs
docker logs <container-id> | grep "shutdown"

# Check if SIGTERM is received
docker kill --signal=TERM <container-id>

# Manual upload test
docker exec <container-id> /db-sync.sh upload
```

### Corrupted Database

**Recovery:**
```bash
# 1. List available backups
aws s3 ls s3://MyProject-database-prod/ | grep backup

# 2. Download known good backup
aws s3 cp s3://MyProject-database-prod/db.sqlite3.backup.TIMESTAMP \
          ./db-good.sqlite3

# 3. Test database integrity
sqlite3 db-good.sqlite3 "PRAGMA integrity_check;"

# 4. Restore to S3
aws s3 cp ./db-good.sqlite3 \
          s3://MyProject-database-prod/db.sqlite3
```

## Testing

### Test Startup Sync

```bash
# 1. Upload test database
echo "test data" > test.db
aws s3 cp test.db s3://MyProject-database-prod/db.sqlite3

# 2. Start container
# Should see: "Database downloaded successfully"

# 3. Verify
docker exec <container-id> cat /app/db.sqlite3
```

### Test Shutdown Sync

```bash
# 1. Start container
# 2. Make database changes via API
# 3. Gracefully stop
docker stop <container-id>  # Sends SIGTERM

# 4. Check S3
aws s3 cp s3://MyProject-database-prod/db.sqlite3 ./test-downloaded.db

# 5. Verify changes are present
```

## Summary

### How Database Saving Works

1. **On Container Start:**
   - Downloads `db.sqlite3` from S3 bucket
   - Django runs migrations
   - Application serves requests using local SQLite

2. **During Operation:**
   - All database operations use local `/app/db.sqlite3`
   - Changes only in container memory

3. **On Container Stop (Graceful):**
   - SIGTERM trap triggers
   - Uploads `/app/db.sqlite3` to S3
   - Creates timestamped backup
   - Container exits

4. **Next Container Start:**
   - Downloads latest `db.sqlite3` from S3
   - Continues with all previous data

### Key Files

- **Sync Script:** `BackEndApi/compose/production/django/db-sync.sh`
- **Entrypoint:** `BackEndApi/compose/production/django/entrypoint.sh`
- **Dockerfile:** `BackEndApi/compose/production/django/Dockerfile`
- **S3 Config:** `terraform/modules/s3/main.tf`
- **IAM Policy:** `terraform/modules/ecs/main.tf` (task role)

### Current Status

✅ **Working:** Startup download, graceful shutdown upload, timestamped backups, S3 versioning

⚠️ **Limitation:** Data loss if container crashes or receives SIGKILL

💡 **Recommended:** Implement periodic sync for production use
