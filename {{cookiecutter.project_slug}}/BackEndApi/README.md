# {{ cookiecutter.project_name }} - Backend API

Django REST Framework backend with WebSocket support via Channels.

## Tech Stack

- **Python {{ cookiecutter.python_version }}**
  - Django REST Framework
  - Django Channels (WebSocket support)
  - Celery (background tasks)
- **Docker & Docker Compose**
- **PostgreSQL** (database)
- **Redis** (caching, Celery broker, WebSocket layer)
- **AWS** (S3, deployment)

## Features

- JWT authentication with refresh tokens
- WebSocket support for real-time features
- Background task processing with Celery
- S3 integration for file uploads
- Comprehensive test setup with pytest
- Example CRUD module (`items`) demonstrating patterns

## Quick Start

1. **Copy environment files:**
   ```bash
   cp -r .envs.example/.local .envs/.local
   ```

2. **Edit environment variables:**
   ```bash
   vim .envs/.local/.django  # Set DJANGO_SECRET_KEY, etc.
   ```

3. **Build and start:**
   ```bash
   make build
   make migrate
   make up
   ```

4. **Access the API:**
   - API: http://localhost:8000/api/v1/
   - Admin: http://localhost:8000/admin/

## Environments

Environment variables are structured in files like:
```
.envs/{env}/.cloud   # AWS credentials
.envs/{env}/.db      # Database credentials
.envs/{env}/.django  # Django settings
```

New environment files should be registered in the docker compose file:
```yaml
env_file:
  - ./.envs/.local/.django
  - ./.envs/.local/.db
  - ./.envs/.local/.cloud
```

## Relevant Commands

All relevant commands are in the `makefile`:

| Command | Description |
|---------|-------------|
| `make build` | Build Docker containers |
| `make up` | Start the application |
| `make down` | Stop the application |
| `make migrate` | Run Django migrations |
| `make makemigrations` | Create new migrations |
| `make shell` | Django shell |
| `make test` | Run tests |
| `make logs` | View container logs |

## Project Structure

```
BackEndApi/
├── src/
│   ├── api/
│   │   ├── items/      # Example CRUD module
│   │   ├── users/      # Authentication & user management
│   │   ├── ws/         # WebSocket handlers
│   │   └── utils/      # Shared utilities
│   └── config/         # Django settings
├── compose/            # Docker configurations
│   ├── local/          # Local development
│   └── production/     # Production deployment
├── requirements/       # Python dependencies
│   ├── base.txt        # Core dependencies
│   ├── local.txt       # Development dependencies
│   └── production.txt  # Production dependencies
├── .envs/              # Environment variables (not in git)
├── .envs.example/      # Example environment files
└── makefile            # Common commands
```

## API Modules

### Users (`/api/v1/users/`)
- Authentication (login, signup, token refresh)
- User profile management
- GitHub OAuth integration

### Items (`/api/v1/items/`) - Example Module
- Full CRUD operations
- Demonstrates ViewSet patterns
- Custom actions (archive, activate)
- Celery task examples

## Testing

```bash
# Run all tests
make test

# Run specific test file
docker-compose -f local.yml exec django pytest api/items/tests/test_views.py

# Run with coverage
docker-compose -f local.yml exec django pytest --cov=api
```

## Adding New Modules

1. Create module directory in `src/api/`
2. Add to `INSTALLED_APPS` in `config/settings/base.py`
3. Create URL routes in `config/urls.py`
4. Follow patterns from the `items` module

See `src/api/items/` for a complete example of:
- Models with common patterns
- Serializers for different use cases
- ViewSet with permissions
- Service layer for business logic
- Celery tasks
- Tests with factories
