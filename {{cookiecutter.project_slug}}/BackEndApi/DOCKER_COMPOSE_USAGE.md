# Docker Compose Setup with Celery

## Overview

The project now includes Celery workers and Redis for async task processing. All services are configured in docker-compose files.

## Services

### Local Development (`local.yml`)

1. **postgres** - PostgreSQL database
2. **redis** - Redis server for Celery broker and Channels
3. **django** - Django web application (port 8000)
4. **celeryworker** - Celery worker for processing async tasks
5. **celerybeat** - Celery beat scheduler for periodic tasks

### Production (`prod.yml`)

1. **redis** - Redis server
2. **django** - Django web application (port 8000)
3. **celeryworker** - Celery worker
4. **celerybeat** - Celery beat scheduler

## Running the Stack

### Local Development

```bash
cd /home/ubuntu/Personal/ProjectMaker/app/BackEndApi

# Build and start all services
docker-compose -f local.yml build
docker-compose -f local.yml up

# Or run in detached mode
docker-compose -f local.yml up -d

# View logs
docker-compose -f local.yml logs -f

# View specific service logs
docker-compose -f local.yml logs -f celeryworker
docker-compose -f local.yml logs -f django

# Stop all services
docker-compose -f local.yml down
```

### Production

```bash
cd /home/ubuntu/Personal/ProjectMaker/app/BackEndApi

# Build and start
docker-compose -f prod.yml build
docker-compose -f prod.yml up -d

# View logs
docker-compose -f prod.yml logs -f

# Stop services
docker-compose -f prod.yml down
```

## Individual Service Management

### Start specific services

```bash
# Start only django and its dependencies
docker-compose -f local.yml up django

# Start only celery worker
docker-compose -f local.yml up celeryworker

# Start without celery beat (if not needed)
docker-compose -f local.yml up django celeryworker
```

### Rebuild specific service

```bash
# Rebuild django (includes celery since they share the same image)
docker-compose -f local.yml build django

# Force rebuild without cache
docker-compose -f local.yml build --no-cache django
```

## Environment Variables

The services expect the following environment files:

### Local Development
- `.envs/.local/.django` - Django settings
- `.envs/.local/.db` - Database credentials
- `.envs/.local/.cloud` - Cloud/AWS settings

Make sure these files exist and contain:

**`.envs/.local/.django`**
```bash
DJANGO_DEBUG=True
DJANGO_SECRET_KEY=your-secret-key
REDIS_URL=redis://redis:6379/0
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key
```

**`.envs/.local/.db`**
```bash
DB_NAME=projectmaker
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=postgres
```

### Production
- `.envs/.prod/.django`
- `.envs/.prod/.db`
- `.envs/.prod/.cloud`

## Testing Celery

### 1. Check if services are running

```bash
docker-compose -f local.yml ps
```

You should see all services (postgres, redis, django, celeryworker, celerybeat) running.

### 2. Check Celery worker logs

```bash
docker-compose -f local.yml logs -f celeryworker
```

You should see:
```
celery@... ready.
```

### 3. Check Redis connection

```bash
docker-compose -f local.yml exec redis redis-cli ping
```

Should return: `PONG`

### 4. Test with Django shell

```bash
docker-compose -f local.yml exec django python manage.py shell
```

Then in the shell:
```python
from api.agents.tasks import process_agent_message
from api.agents.models import Message

# Get a message ID
message = Message.objects.first()
if message:
    # Queue the task
    result = process_agent_message.delay(message.id)
    print(f"Task ID: {result.id}")
```

### 5. Test the full flow

See `CELERY_SETUP.md` for complete testing instructions with WebSocket.

## Monitoring

### View active tasks

```bash
docker-compose -f local.yml exec celeryworker celery -A config.celery_app inspect active
```

### View registered tasks

```bash
docker-compose -f local.yml exec celeryworker celery -A config.celery_app inspect registered
```

### View worker stats

```bash
docker-compose -f local.yml exec celeryworker celery -A config.celery_app inspect stats
```

## Troubleshooting

### Celery worker not starting

1. Check logs: `docker-compose -f local.yml logs celeryworker`
2. Verify Redis is running: `docker-compose -f local.yml ps redis`
3. Rebuild the image: `docker-compose -f local.yml build django`

### Tasks not executing

1. Check if worker is connected to Redis:
   ```bash
   docker-compose -f local.yml exec celeryworker celery -A config.celery_app inspect ping
   ```
2. Check Redis logs: `docker-compose -f local.yml logs redis`
3. Verify REDIS_URL environment variable

### WebSocket not working

1. Check Django logs: `docker-compose -f local.yml logs django`
2. Verify Redis is running for Channels
3. Check CHANNEL_LAYERS configuration in settings

### Database connection errors

1. Ensure postgres is running: `docker-compose -f local.yml ps postgres`
2. Check database environment variables
3. Run migrations: `docker-compose -f local.yml exec django python manage.py migrate`

## Scaling Workers

You can scale the number of Celery workers:

```bash
# Run 3 worker instances
docker-compose -f local.yml up --scale celeryworker=3
```

## Stopping and Cleaning Up

```bash
# Stop all services
docker-compose -f local.yml down

# Stop and remove volumes (CAREFUL: deletes database data)
docker-compose -f local.yml down -v

# Remove all containers, networks, and images
docker-compose -f local.yml down --rmi all
```

## Development Workflow

Typical workflow when making changes:

1. **Code changes** - Edit Python files
2. **Restart services** - Changes are auto-reloaded for Django
3. **For Celery changes** - Restart worker:
   ```bash
   docker-compose -f local.yml restart celeryworker
   ```
4. **For dependency changes** - Rebuild:
   ```bash
   docker-compose -f local.yml build django
   docker-compose -f local.yml up -d
   ```

## Quick Commands Reference

```bash
# Start everything
docker-compose -f local.yml up -d

# View all logs
docker-compose -f local.yml logs -f

# Restart a service
docker-compose -f local.yml restart celeryworker

# Execute command in container
docker-compose -f local.yml exec django python manage.py shell

# Stop everything
docker-compose -f local.yml down

# Rebuild
docker-compose -f local.yml build
```
